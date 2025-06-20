
# Create your models here.
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    is_user = models.BooleanField(default=False)
    is_dietician = models.BooleanField(default=False)

    class Meta:
        verbose_name = "CustomUser"

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile = models.PositiveIntegerField(
        validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)]
    )
    gender_choices = (("Male", "Male"), ("Female", "Female"), ("Other", "Other"))
    gender = models.CharField(max_length=10, choices=gender_choices)
    dob = models.DateField(null=True, default=None)
    photo = models.ImageField(upload_to="images", null=True, blank=True, default='images/default_profile.jpg')
    # Inside UserProfile model
    height = models.FloatField(help_text="Height in centimeters", null=True, blank=True)
    weight = models.FloatField(help_text="Weight in kilograms", null=True, blank=True)

    activity_level_choices = [
    ("Sedentary", "Sedentary (little or no exercise)"),
    ("Lightly active", "Lightly active (light exercise/sports 1-3 days/week)"),
    ("Moderately active", "Moderately active (moderate exercise 3-5 days/week)"),
    ("Very active", "Very active (hard exercise 6-7 days/week)"),
    ("Extra active", "Extra active (very hard exercise & physical job)"),
]

    activity_level = models.CharField(max_length=20, choices=activity_level_choices, null=True, blank=True)

    goal_choices = [
        ("Lose Weight", "Lose Weight"),
        ("Maintain Weight", "Maintain Weight"),
        ("Gain Muscle", "Gain Muscle"),
    ]
    goal = models.CharField(max_length=20, choices=goal_choices, null=True, blank=True)

    dietary_preference_choices = [
        ("Vegetarian", "Vegetarian"),
        ("Non-Vegetarian", "Non-Vegetarian"),
        ("Vegan", "Vegan"),
        ("Keto", "Keto"),
        ("Other", "Other"),
    ]
    dietary_preference = models.CharField(max_length=20, choices=dietary_preference_choices, null=True, blank=True)

    target_weight = models.FloatField(help_text="Target weight in kg", null=True, blank=True)

    medical_conditions = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)



class DieticianProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    photo = models.ImageField(upload_to="images", null=True, default=None)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class HealthLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField()
    height = models.FloatField()
    water_intake = models.FloatField()
    calories = models.PositiveIntegerField()
    sleep_hours = models.FloatField()
    steps = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_appointments")
    dietician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dietician_appointments")
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} with {self.dietician.username} on {self.date}"

