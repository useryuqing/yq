from rest_framework import serializers
from xth.models import Product,SlideShow,MainDescription


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id","name","longName","productId","storeNums","specifics","sort","marketPrice","price","categoryId","childId","img","keywords","brandId","brandName","safeDay","safeUnit","safeUnitDesc")


class SlideShowSerializers(serializers.ModelSerializer):
    class Meta:
        model = SlideShow
        fields = ("trackid","name","img","sort")


class MainDescriptionSerializers(serializers.ModelSerializer):
    class Meta:
        model = MainDescription
        fields = ("categoryId","categoryName","sort","img","product1","product2","product3")