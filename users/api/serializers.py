# serializers.py
from rest_framework import serializers
from vehicles.models import VehicleType
from users.models import Customer, User
from base.utils.generate_otp import generate_otp

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    vehicle_type = serializers.IntegerField(required=False)
    number_plate = serializers.CharField(required=False)
    insurance_document = serializers.FileField(required=False)
    noc_document = serializers.FileField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'user_type', 'age', 'address', 'profile_image',
                  'vehicle_type', 'number_plate', 'insurance_document', 'noc_document']

    def validate(self, attrs):
        user_type = attrs.get("user_type")
        phone_number = attrs.get("phone_number")
        age = attrs.get("age")
        password = attrs.get("password")
        email = attrs.get("email")

        if not isinstance(user_type, str) or user_type.lower() not in ["owner", "customer"]:
            raise serializers.ValidationError({"user_type": "Enter a valid user type: 'owner' or 'customer'."})

        if len(phone_number) < 10:
            raise serializers.ValidationError({"phone_number": "Enter a valid phone number."})

        if not isinstance(age, int) or age < 17:
            raise serializers.ValidationError({"age": "Enter a valid age."})

        if not isinstance(password, str) or len(password) < 6:
            raise serializers.ValidationError({"password": "Password must be at least 6 characters."})

        if not isinstance(email, str) or User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Enter a valid and unused email."})
        
        if user_type.lower() == "customer":
            if not attrs.get('vehicle_type'):
                raise serializers.ValidationError({"vehicle_type": "Vehicle type is required for customers."})
            if not attrs.get('number_plate'):
                raise serializers.ValidationError({"number_plate": "Number plate is required for customers."})
            if not attrs.get('insurance_document'):
                raise serializers.ValidationError({"insurance_document": "Insurance document is required for customers."})

        return attrs

    def create(self, validated_data):
        user_type = validated_data.get('user_type')
        password = validated_data.pop('password')

        vehicle_type_id = validated_data.pop('vehicle_type', None)
        number_plate = validated_data.pop('number_plate', None)
        insurance_document = validated_data.pop('insurance_document', None)
        noc_document = validated_data.pop('noc_document', None)

        user = User(**validated_data)
        user.set_password(password)
        user.otp=generate_otp()
        user.save()

        if user_type.lower() == "customer":
            vehicle_tobj = VehicleType.objects.get(id=vehicle_type_id)
            customer = Customer.objects.create(
                user=user,
                vehicle_type=vehicle_tobj,
                number_plate=number_plate,
                insurance_document=insurance_document,
                noc_document=noc_document
            )
            customer.save()

        return user