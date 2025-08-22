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
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'password', 'user_type', 'age', 'address', 'profile_image',
                  'vehicle_type']

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
        full_name = attrs.get("full_name")
        if not full_name:
            raise serializers.ValidationError({"full_name": "Enter a valid User Name."})
        if not isinstance(user_type, str) or user_type.lower() not in [User.ParkingOwner,User.Customer]:
            raise serializers.ValidationError({"user_type": "Enter a valid user type: 'owner' or 'customer'."})
        

        if len(phone_number) < 10:
            raise serializers.ValidationError({"phone_number": "Enter a valid phone number."})
        if  User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "phone number already registered.."})


        if not isinstance(age, int) or age < 17:
            raise serializers.ValidationError({"age": "Enter a valid age."})

        if not isinstance(password, str) or len(password) < 6:
            raise serializers.ValidationError({"password": "Password must be at least 6 characters."})

        if not isinstance(email, str) :
            raise serializers.ValidationError({"email": "Enter a valid and unused email."})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Enter a valid unused email."})
        
        if user_type.lower() == "customer":
            if not attrs.get('vehicle_type'):
                raise serializers.ValidationError({"vehicle_type": "Vehicle type is required for customers."})


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

        user = User(**validated_data)
        user.set_password(password)
        user.otp=generate_otp()
        user.save()

        if user_type.lower() == "customer":

            vehicle_tobj = VehicleType.objects.get(id=vehicle_type_id)
            customer = Customer.objects.create(
                user=user,
                vehicle_type=vehicle_tobj,
            )
            customer.save()
        return user

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'password', 'age', 'address', 'profile_image']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},  # allow update without password
        }

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        age = attrs.get("age")
        password = attrs.get("password")
        email = attrs.get("email")
        full_name = attrs.get("full_name")

        instance = getattr(self, 'instance', None)  

        if instance:  
            if 'email' in attrs and attrs['email'] != instance.email:
                raise serializers.ValidationError({"email": "Email cannot be changed."})

            if 'phone_number' in attrs and attrs['phone_number'] != instance.phone_number:
                raise serializers.ValidationError({"phone_number": "Phone number cannot be changed."})

        if not full_name:
            raise serializers.ValidationError("Enter a valid User Name.")

        if not phone_number or len(phone_number) < 10:
            raise serializers.ValidationError("Enter a valid phone number.")

        user_id = self.instance.id if self.instance else None
        if User.objects.filter(phone_number=phone_number).exclude(id=user_id).exists():
            raise serializers.ValidationError("Phone number already registered.")

        if age is not None and (not isinstance(age, int) or age < 17):
            raise serializers.ValidationError("Enter a valid age.")

        if password and (not isinstance(password, str) or len(password) < 6):
            raise serializers.ValidationError("Password must be at least 6 characters.")

        if email and User.objects.filter(email=email).exclude(id=user_id).exists():
            raise serializers.ValidationError("Enter a valid and unused email.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")  # get request from context
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.user_type = User.Admin

        if request and hasattr(request, "user"):
            user.created_by = request.user
            user.updated_by = request.user

        user.is_verified = True
        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get("request")  

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if request and hasattr(request, "user"):
            instance.updated_by = request.user

        instance.save()
        return instance


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'password', 'age', 'address', 'profile_image']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},  # allow update without password
        }

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        age = attrs.get("age")
        password = attrs.get("password")
        email = attrs.get("email")
        full_name = attrs.get("full_name")

        instance = getattr(self, 'instance', None)  

        if instance:  
            if 'email' in attrs and attrs['email'] != instance.email:
                raise serializers.ValidationError({"email": "Email cannot be changed."})

            if 'phone_number' in attrs and attrs['phone_number'] != instance.phone_number:
                raise serializers.ValidationError({"phone_number": "Phone number cannot be changed."})

        if not full_name:
            raise serializers.ValidationError("Enter a valid User Name.")

        if not phone_number or len(phone_number) < 10:
            raise serializers.ValidationError("Enter a valid phone number.")

        user_id = self.instance.id if self.instance else None
        if User.objects.filter(phone_number=phone_number).exclude(id=user_id).exists():
            raise serializers.ValidationError("Phone number already registered.")

        if age is not None and (not isinstance(age, int) or age < 17):
            raise serializers.ValidationError("Enter a valid age.")

        if password and (not isinstance(password, str) or len(password) < 6):
            raise serializers.ValidationError("Password must be at least 6 characters.")

        if email and User.objects.filter(email=email).exclude(id=user_id).exists():
            raise serializers.ValidationError("Enter a valid and unused email.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")  # get request from context
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.user_type = User.ParkingOwner

        if request and hasattr(request, "user"):
            user.created_by = request.user
            user.updated_by = request.user

        user.is_verified = True
        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get("request")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if request and hasattr(request, "user"):
            instance.updated_by = request.user

        instance.save()
        return instance
