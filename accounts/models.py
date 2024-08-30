from django.db import models
from django.contrib.auth.models import User

# Friend Request Model

class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    is_accepted = models.BooleanField(default=False)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['sender', 'receiver']
        db_table = 'friend_request'

    def __str__(self):
        return f"Sender: {self.sender.first_name} {self.sender.last_name} => Receiver: {self.receiver.first_name} {self.receiver.last_name}"

