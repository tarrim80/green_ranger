<template>
  <div>
    <v-row align="center">
      <v-col>
        <h2 class="text-h5">Виды дефектов</h2>
      </v-col>
    </v-row>
    <v-row align="center">
      <v-col>
        <v-btn color="primary" @click="openCreateForm">Создать вид дефекта</v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-data-table
          :headers="headers"
          :items="defectTypes"
          :loading="loading"
          class="elevation-1"
          items-per-page-text="Показывать по"
        >
          <template v-slot:item.images="{ item }">
            <v-icon
              v-if="item.images && item.images.length > 0"
              @click="openGallery(item.images)"
            >
              mdi-image-multiple
            </v-icon>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-icon small class="mr-2" @click="openEditForm(item)">mdi-pencil</v-icon>
            <v-icon small @click="deleteDefectType(item)">mdi-delete</v-icon>
          </template>
          <template v-slot:no-data>
            <div class="text-center py-4">Нет элементов для отображения</div>
          </template>
        </v-data-table>
      </v-col>
    </v-row>

    <v-dialog v-model="galleryDialog" max-height="80%" max-width="800px">
      <v-card>
        <v-card-text>
          <photo-gallery :items="selectedImages" readonly />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="galleryDialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useDefectTypeStore } from '@/stores/defectTypeStore';
import { useUiStore } from '@/stores/uiStore';
import DefectTypeForm from '@/components/DefectTypeForm.vue';
import PhotoGallery from '@/components/PhotoGallery.vue';
import { defectTypeService } from '@/services/defectTypeService';

const defectTypeStore = useDefectTypeStore();
const uiStore = useUiStore();

const galleryDialog = ref(false);
const selectedImages = ref([]);

const headers = [
  { title: 'Название', value: 'name' },
  { title: 'Описание', value: 'description' },
  { title: 'Фото', value: 'images', sortable: false, align: 'center' },
  { title: 'Действия', value: 'actions', sortable: false },
];

const defectTypes = computed(() => defectTypeStore.getDefectTypes);
const loading = computed(() => defectTypeStore.loading);

onMounted(() => {
  defectTypeStore.fetchDefectTypes();
});

const openGallery = (images) => {
  selectedImages.value = images;
  galleryDialog.value = true;
};

const handleSave = async (payload) => {
  try {
    const id = uiStore.panelProps.initialData?.id;
    if (id) {
      await defectTypeStore.updateDefectType(id, payload);
    } else {
      await defectTypeStore.createDefectType(payload);
    }
    await defectTypeStore.refreshDefectTypes();
    uiStore.closePanel();
  } catch (error) {
    const errorDetail = error.response?.data?.detail || 'Произошла непредвиденная ошибка.';
    uiStore.showInfoDialog('Ошибка сохранения', errorDetail);
  }
};

const handleDeletePhoto = async (photoId) => {
  try {
    await defectTypeStore.removePhoto(photoId);
    const id = uiStore.panelProps.initialData.id;
    const response = await defectTypeService.getDefectTypeById(id);
    uiStore.updatePanelProps({ initialData: response.data });
  } catch (error) {
    uiStore.showInfoDialog('Ошибка', 'Не удалось удалить фотографию.');
  }
};

const openCreateForm = () => {
  const props = {
    initialData: {},
    onSubmit: handleSave,
    onCancel: () => uiStore.closePanel(),
    onDeletePhoto: handleDeletePhoto,
  };
  uiStore.openPanel(DefectTypeForm, 'Создать вид дефекта', props);
};

const openEditForm = (item) => {
  const props = {
    initialData: { ...item },
    onSubmit: handleSave,
    onCancel: () => uiStore.closePanel(),
    onDeletePhoto: handleDeletePhoto,
  };
  uiStore.openPanel(DefectTypeForm, 'Редактировать вид дефекта', props);
};

const deleteDefectType = (item) => {
  uiStore.showConfirmDialog({
    title: 'Подтвердите удаление',
    text: `Вы уверены, что хотите удалить вид дефекта "${item.name}"?`,
    onConfirm: async () => {
      try {
        await defectTypeStore.deleteDefectType(item.id);
        await defectTypeStore.refreshDefectTypes();
      } catch (error) {
        const errorDetail = error.response?.data?.detail || "Произошла ошибка";
        uiStore.showInfoDialog('Ошибка удаления', errorDetail);
      }
    }
  });
};
</script>