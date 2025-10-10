from django.urls import path
from . import views

app_name = 'vetements'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='user_profile'),

    # Main pages
    path('', views.accueil, name='accueil'),
    path('vetements/', views.VetementListView.as_view(), name='liste_vetements'),
    path('vetements/<int:pk>/', views.VetementDetailView.as_view(), name='detail_vetement'),
    path('categorie/<int:categorie_id>/', views.vetements_par_categorie, name='categorie'),
    path('entretien/', views.entretien, name='entretien'),
    path('tenues/', views.tenues_list, name='tenues_list'),
    path('tenues/<int:pk>/', views.tenue_detail, name='tenue_detail'),
    path('fring/', views.fring_widget, name='fring_widget'),
    path('valises/', views.valises_list, name='valises_list'),
    path('valises/<int:pk>/', views.valise_detail, name='valise_detail'),
    path('statistiques/', views.statistiques, name='statistiques'),

    # Messaging
    path('messages/', views.messages_inbox, name='messages_inbox'),
    path('messages/sent/', views.messages_sent, name='messages_sent'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('messages/compose/', views.message_compose, name='message_compose'),
    path('messages/compose/<int:destinataire_id>/', views.message_compose, name='message_compose_to'),
    path('messages/reply/<int:repondre_a>/', views.message_compose, name='message_reply'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),

    # Amis
    path('amis/', views.amis_list, name='amis_list'),
    path('amis/demander/<int:user_id>/', views.amitie_demander, name='amitie_demander'),
    path('amis/accepter/<int:amitie_id>/', views.amitie_accepter, name='amitie_accepter'),
    path('amis/refuser/<int:amitie_id>/', views.amitie_refuser, name='amitie_refuser'),
    path('amis/supprimer/<int:amitie_id>/', views.amitie_supprimer, name='amitie_supprimer'),

    # Marketplace
    path('marketplace/', views.marketplace_liste, name='marketplace_liste'),
    path('marketplace/mes-annonces/', views.marketplace_mes_annonces, name='marketplace_mes_annonces'),
    path('marketplace/annonce/<int:annonce_id>/', views.marketplace_annonce_detail, name='marketplace_annonce_detail'),
    path('marketplace/creer/<int:vetement_id>/', views.marketplace_creer_annonce, name='marketplace_creer_annonce'),
    path('marketplace/modifier/<int:annonce_id>/', views.marketplace_modifier_annonce, name='marketplace_modifier_annonce'),
    path('marketplace/supprimer/<int:annonce_id>/', views.marketplace_supprimer_annonce, name='marketplace_supprimer_annonce'),
]
