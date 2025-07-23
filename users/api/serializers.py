# serializers.py
from rest_framework import serializers
from vehicles.models import VehicleType
from users.models import Customer, User
from base.utils.generate_otp import generate_otp

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles creation of both 'owner' and 'customer' users. For 'customer' user_type,
    vehicle details must also be provided.
    """
    password = serializers.CharField(write_only=True)
    vehicle_type = serializers.IntegerField(required=False)
    number_plate = serializers.CharField(required=False)
    licence_number = serializers.CharField(required=False)
    rc_book_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'password', 'user_type', 'age', 'address', 'profile_image',
                  'vehicle_type', 'number_plate', 'licence_number', 'rc_book_number']

    def validate(self, attrs):
        """
        Validate input fields for registration.

        Ensures:
        - Required fields are present and valid.
        - Email is unique.
        - Password meets minimum length.
        - For 'customer' type, vehicle and license information is required.

        Returns:
            dict: Validated data.

        Raises:
            serializers.ValidationError: If validation fails.
        """
        user_type = attrs.get("user_type")
        phone_number = attrs.get("phone_number")
        age = attrs.get("age")
        password = attrs.get("password")
        email = attrs.get("email")
        number_plate = attrs.get('number_plate',"")
        licence_number = attrs.get('licence_number','')
        rc_book_number = attrs.get('rc_book_number','')
        full_name = attrs.get("full_name")
        if not full_name:
            raise serializers.ValidationError({"full_name": "Enter a valid User Name."})
        if not isinstance(user_type, str) or user_type.lower() not in ["owner", "customer"]:
            raise serializers.ValidationError({"user_type": "Enter a valid user type: 'owner' or 'customer'."})
        if user_type.lower()  == "customer":
            if  not number_plate :
                raise serializers.ValidationError({"number_plate": "Enter a valid Number Plate."})
            if not licence_number:
                raise serializers.ValidationError({"licence_number": "Enter a valid Licence Number."})

            if not rc_book_number :
                raise serializers.ValidationError({"rc_book_number": "Enter a valid rc book number."})

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
            
        return attrs

    def create(self, validated_data):
        """
        Create a new user instance.

        Sets password, generates OTP, and for customer users, creates related Customer record.

        Args:
            validated_data (dict): Validated registration data.

        Returns:
            User: The created user instance.
        """
        user_type = validated_data.get('user_type')
        password = validated_data.pop('password')
        vehicle_type_id = validated_data.pop('vehicle_type', None)
        number_plate = validated_data.pop('number_plate', None)
        licence_number = validated_data.pop('licence_number', None)
        rc_book_number = validated_data.pop('rc_book_number', None)

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
                licence_number=licence_number,
                rc_book_number=rc_book_number
            )
            customer.save()

        return user