from django.db import models

class SexPet(models.TextChoices):
    MALE = "Male",
    FEMALE = "Female",
    NOT_INFORMED = "Not Informed"

class Pet(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    weight = models.FloatField(max_length=50, null= False)
    sex = models.CharField(max_length=20, choices = SexPet.choices, default = SexPet.NOT_INFORMED)

    group = models.ForeignKey("groups.Group", on_delete=models.PROTECT, related_name="pets", null=True)
    traits = models.ManyToManyField("traits.Trait", related_name="pets")

    def __repr__(self) -> str:
        return f"<[{self.id}] {self.name} - {self.age}yGears - {self.weight}kg - {self.sex} - {self.group} - {self.traits}>"
