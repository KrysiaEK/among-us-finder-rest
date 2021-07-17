from django.contrib import admin
from .models import Room, Message


@admin.register(Room)
class Room(admin.ModelAdmin):
	pass


@admin.register(Message)
class Message(admin.ModelAdmin):
	pass
