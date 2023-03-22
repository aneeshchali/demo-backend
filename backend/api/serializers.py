from rest_framework import serializers

from user.models import Doctor,User

class DocDetailsSerializers(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    class Meta:
        model = Doctor
        fields = ["user","img", "phone","user_name", "qualification", "speciality", "hosp_name", "experience", "fees", "slot_start",
                  "slot_end", "age", "gender"]

    def get_user_name(self,obj):
        return obj.user.name

class DocSpecialistSerializers(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["speciality"]

