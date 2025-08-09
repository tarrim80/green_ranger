<template>
  <v-form @submit.prevent="submitForm">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="form.name"
            label="Название"
            :rules="[rules.required]"
            required
            density="compact"
            hide-details="auto"
            variant="outlined"
          ></v-text-field>
        </v-col>
        <v-col cols="12">
          <v-textarea
            v-model="form.description"
            label="Описание"
            density="compact"
            hide-details="auto"
            variant="outlined"
          ></v-textarea>
        </v-col>
      </v-row>

      <v-row v-if="isEditMode && form.existingImages && form.existingImages.length > 0">
        <v-col
          v-for="image in form.existingImages"
          :key="image.id"
          cols="auto"
        >
          <div class="thumbnail-container">
            <v-img
              :src="image.thumbnail_path"
              :lazy-src="image.thumbnail_path"
              aspect-ratio="1"
              width="100"
              height="100"
              contain
              class="rounded border"
            ></v-img>
            <v-btn
              icon
              size="x-small"
              class="delete-btn"
              @click="handleDeletePhoto(image.id)"
              title="Удалить изображение"
            >
              <v-icon>mdi-close-circle</v-icon>
            </v-btn>
          </div>
        </v-col>
      </v-row>

      <v-row align="center">
        <v-col cols="12">
            <v-file-input
                ref="fileInput"
                v-model="newlySelectedFiles"
                multiple
                accept="image/*"
                class="d-none"
            ></v-file-input>
            <v-btn @click="triggerFileInput">
                <v-icon left>mdi-camera</v-icon>
                <v-icon>mdi-plus</v-icon>
                Добавить фото
            </v-btn>
        </v-col>
        <v-col cols="12" v-if="form.newPhotos.length > 0">
             <div class="d-flex flex-wrap ga-2">
                <v-chip
                    v-for="(file, index) in form.newPhotos"
                    :key="index"
                    closable
                    @click:close="removeNewPhoto(index)"
                >
                    {{ file.name }}
                </v-chip>
            </div>
        </v-col>
      </v-row>

    </v-container>
    <v-card-actions class="px-4">
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="props.onCancel">Отмена</v-btn>
      <v-btn color="primary" variant="flat" type="submit">{{ isEditMode ? 'Сохранить' : 'Создать' }}</v-btn>
    </v-card-actions>
  </v-form>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ name: '', description: '', images: [] }),
  },
  onSubmit: { type: Function, required: true },
  onCancel: { type: Function, required: true },
  onDeletePhoto: { type: Function, required: true },
});

const isEditMode = computed(() => !!props.initialData.id);
const fileInput = ref(null);
const newlySelectedFiles = ref([]);

const form = ref({
  name: '',
  description: '',
  newPhotos: [],
  existingImages: [],
});

const rules = {
  required: value => !!value || 'Поле обязательно для заполнения',
};

watch(() => props.initialData, (newData) => {
  if (newData && newData.id) {
    form.value.name = newData.name || '';
    form.value.description = newData.description || '';
    form.value.existingImages = newData.images || [];
    form.value.newPhotos = [];
  } else {
    form.value.name = '';
    form.value.description = '';
    form.value.existingImages = [];
    form.value.newPhotos = [];
  }
}, { immediate: true, deep: true });

watch(newlySelectedFiles, (selection) => {
  if (selection.length > 0) {
    form.value.newPhotos.push(...selection);
    newlySelectedFiles.value = []; 
  }
});

const triggerFileInput = () => {
  fileInput.value.click();
};

const removeNewPhoto = (index) => {
  form.value.newPhotos.splice(index, 1);
};

const submitForm = () => {
  if (isEditMode.value) {
    const payload = {
      textData: {
        name: form.value.name,
        description: form.value.description,
      },
      newPhotos: form.value.newPhotos || [],
    };
    props.onSubmit(payload);
  } else {
    const formData = new FormData();
    formData.append('name', form.value.name);
    formData.append('description', form.value.description);
    
    if (form.value.newPhotos && form.value.newPhotos.length > 0) {
      for (const photo of form.value.newPhotos) {
        formData.append('files', photo);
      }
    }
    props.onSubmit(formData);
  }
};

const handleDeletePhoto = (photoId) => {
    props.onDeletePhoto(photoId);
}

</script>

<style scoped>
.thumbnail-container {
  position: relative;
  display: inline-block;
}

.delete-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background-color: rgba(255, 255, 255, 0.8);
}
</style>
