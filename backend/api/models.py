from django.db import models

class ScanHistory(models.Model):
    scan_type = models.CharField(max_length=50) # 'url' ou 'email'
    content = models.TextField()
    verdict = models.CharField(max_length=50) # 'PHISHING' ou 'SÉCURISÉ'
    risk_score = models.FloatField()
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
