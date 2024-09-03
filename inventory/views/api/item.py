from rest_framework import generics, serializers, permissions

from inventory.models import EbayItem


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayItem
        fields = '__all__'


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EbayItem.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        serialized = self.serializer_class(data=request.data, partial=True)
        return super().partial_update(request, *args, **kwargs)
