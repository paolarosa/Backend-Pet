from django.shortcuts import render
from rest_framework.views import APIView, Response, status
from pets.models import Pet
from pets.serializers import PetSerializer
from pet_kare.pagination import CustomPageNumberPagination
from groups.models import Group
from traits.models import Trait
from django.shortcuts import get_object_or_404

class PetView(APIView, CustomPageNumberPagination):
    def post(self, request):
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        groups = serializer.validated_data.pop("group")
        group_obj = Group.objects.filter(
            scientific_name__icontains=groups["scientific_name"]
        ).first()
        if not group_obj:
            group_obj = Group.objects.create(**groups)

        traits = serializer.validated_data.pop("traits")
        pet = Pet.objects.create(**serializer.validated_data, group=group_obj)
        
        for trait in traits:
            trait_obj = Trait.objects.filter(
                name__iexact=trait["name"]
            ).first()
            if not trait_obj:
                trait_obj = Trait.objects.create(**trait)
            pet.traits.add(trait_obj)
        
        serializer = PetSerializer(pet)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        trait = request.query_params.get("trait", None)
        if trait:
            pets = Pet.objects.filter(
                traits__name=trait
            )
        else:
            pets = Pet.objects.all()
            
        result_page = self.paginate_queryset(pets, request, view=self)
        serializer= PetSerializer(result_page, many=True)
        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def get(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_200_OK) 

    def delete(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        groups = serializer.validated_data.pop("group", None)
        traits = serializer.validated_data.pop("traits", None)

        if groups:
            try:
                group_obj = Group.objects.get(
                    scientific_name__icontains=groups["scientific_name"]
                )
            except Group.DoesNotExist:
                group_obj = Group.objects.create(**groups)
            pet.group = group_obj
        
        if traits:
            trait_list = []
            for trait in traits:
                try:
                    trait_obj = Trait.objects.get(
                        name__iexact=trait["name"]
                    )#.first()
                except Trait.DoesNotExist:
                    trait_obj = Trait.objects.create(**trait)
                trait_list.append(trait_obj)
            pet.traits.set(trait_list)

        for key,value in serializer.validated_data.items():
            setattr(pet, key, value)   #seta o atributo de pet dentro da key e value recebida

        pet.save()
        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_200_OK)