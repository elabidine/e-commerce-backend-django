from djoser.serializers import UserCreateSerializer as BaseCreateSerializer
from djoser.serializers import UserCreateSerializer as BaseSerializer



class UserCreateSerializer(BaseCreateSerializer):
    class Meta(BaseSerializer.Meta):
        fields = ['id','username','email','password','first_name','last_name']

class UserSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        fields = ['id','username','email','first_name','last_name']
