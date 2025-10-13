"""
Custom storage backend pour uploader les fichiers vers Unraid via SFTP
"""

import os
import paramiko
from io import BytesIO
from django.core.files.storage import Storage
from django.conf import settings
from django.utils.deconstruct import deconstructible
from decouple import config


@deconstructible
class UnraidSFTPStorage(Storage):
    """
    Backend de stockage personnalisé pour uploader les fichiers
    vers le serveur nginx Unraid via SFTP.

    Configuration requise dans settings ou .env :
    - UNRAID_SFTP_HOST : IP ou domaine du serveur (ex: 192.168.1.47)
    - UNRAID_SFTP_PORT : Port SSH (défaut: 22)
    - UNRAID_SFTP_USER : Utilisateur SSH (ex: root)
    - UNRAID_SFTP_PASSWORD : Mot de passe (ou utiliser clé SSH)
    - UNRAID_SFTP_KEY_PATH : Chemin vers clé SSH privée (optionnel)
    - UNRAID_MEDIA_PATH : Chemin distant (ex: /mnt/user/appdata/garde-robe/media/)
    - MEDIA_URL : URL publique nginx (ex: https://media.votredomaine.com/media/)
    """

    def __init__(self):
        self.host = config('UNRAID_SFTP_HOST', default='192.168.1.47')
        self.port = config('UNRAID_SFTP_PORT', default=22, cast=int)
        self.username = config('UNRAID_SFTP_USER', default='root')
        self.password = config('UNRAID_SFTP_PASSWORD', default=None)
        self.key_path = config('UNRAID_SFTP_KEY_PATH', default=None)
        self.remote_path = config(
            'UNRAID_MEDIA_PATH',
            default='/mnt/user/appdata/garde-robe/media/'
        )
        self.base_url = config('MEDIA_URL', default='/media/')

    def _get_sftp_client(self):
        """Établir une connexion SFTP"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connexion avec clé SSH ou mot de passe
        if self.key_path and os.path.exists(self.key_path):
            ssh.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                key_filename=self.key_path,
                timeout=10
            )
        elif self.password:
            ssh.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
        else:
            raise ValueError("SFTP credentials not configured (password or key required)")

        return ssh, ssh.open_sftp()

    def _save(self, name, content):
        """Upload un fichier vers Unraid"""
        ssh, sftp = None, None
        try:
            ssh, sftp = self._get_sftp_client()

            # Construire le chemin complet
            remote_file = os.path.join(self.remote_path, name)
            remote_dir = os.path.dirname(remote_file)

            # Créer les répertoires si nécessaire
            self._makedirs_sftp(sftp, remote_dir)

            # Upload le fichier
            if hasattr(content, 'temporary_file_path'):
                # Fichier temporaire sur disque
                sftp.put(content.temporary_file_path(), remote_file)
            else:
                # Fichier en mémoire
                content.seek(0)
                sftp.putfo(content, remote_file)

            # Définir les permissions (lecture pour tous)
            sftp.chmod(remote_file, 0o644)

            return name

        except Exception as e:
            raise IOError(f"Error uploading file to Unraid: {e}")

        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

    def _makedirs_sftp(self, sftp, path):
        """Créer récursivement les répertoires sur SFTP"""
        dirs = []
        while path and path != '/':
            try:
                sftp.stat(path)
                break
            except IOError:
                dirs.append(path)
                path = os.path.dirname(path)

        # Créer les répertoires manquants
        for directory in reversed(dirs):
            try:
                sftp.mkdir(directory)
                sftp.chmod(directory, 0o755)
            except IOError:
                pass  # Répertoire existe déjà

    def _open(self, name, mode='rb'):
        """Télécharger un fichier depuis Unraid (lecture)"""
        ssh, sftp = None, None
        try:
            ssh, sftp = self._get_sftp_client()
            remote_file = os.path.join(self.remote_path, name)

            # Télécharger dans un buffer mémoire
            file_obj = BytesIO()
            sftp.getfo(remote_file, file_obj)
            file_obj.seek(0)

            return file_obj

        except Exception as e:
            raise IOError(f"Error downloading file from Unraid: {e}")

        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

    def exists(self, name):
        """Vérifier si un fichier existe sur Unraid"""
        ssh, sftp = None, None
        try:
            ssh, sftp = self._get_sftp_client()
            remote_file = os.path.join(self.remote_path, name)
            sftp.stat(remote_file)
            return True
        except IOError:
            return False
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

    def delete(self, name):
        """Supprimer un fichier sur Unraid"""
        ssh, sftp = None, None
        try:
            ssh, sftp = self._get_sftp_client()
            remote_file = os.path.join(self.remote_path, name)
            sftp.remove(remote_file)
        except IOError:
            pass  # Fichier n'existe pas
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

    def size(self, name):
        """Obtenir la taille d'un fichier"""
        ssh, sftp = None, None
        try:
            ssh, sftp = self._get_sftp_client()
            remote_file = os.path.join(self.remote_path, name)
            return sftp.stat(remote_file).st_size
        except IOError:
            return 0
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

    def url(self, name):
        """Retourner l'URL publique du fichier via nginx"""
        if not name:
            return ''
        return f"{self.base_url.rstrip('/')}/{name}"

    def listdir(self, path):
        """Lister les fichiers d'un répertoire"""
        ssh, sftp = None, None
        try:
            ssh, sftp = self._get_sftp_client()
            remote_path = os.path.join(self.remote_path, path) if path else self.remote_path

            files = []
            dirs = []

            for item in sftp.listdir_attr(remote_path):
                if item.st_mode & 0o040000:  # Répertoire
                    dirs.append(item.filename)
                else:  # Fichier
                    files.append(item.filename)

            return dirs, files

        except IOError:
            return [], []

        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
