<template>
  <v-container>
    <v-row v-if="items && items.length > 0" dence>
      <v-col>
        <v-carousel show-arrows="hover" hide-delimiters height="60vh">
          <v-carousel-item
            v-for="item in items"
            :key="item.id"
            :src="item.file_path"
            @click="openDialog(item.file_path)"
            contain
          >
            <div v-if="!props.readonly" class="d-flex fill-height justify-end align-start pa-2">
                <v-btn icon="mdi-delete" size="small" color="error" @click.stop="emit('delete-photo', item.id)"></v-btn>
            </div>
          </v-carousel-item>
        </v-carousel>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col>
        <p>Нет доступных фотографий.</p>
      </v-col>
    </v-row>

    <v-dialog 
      v-model="dialog" 
    >
      <v-card >
        <v-img :src="dialogImageUrl" class="dialog-image" cover
          ></v-img>
        <v-card-actions class="justify-center flex-shrink-0">
          <v-btn text @click="dialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['delete-photo']);

const dialog = ref(false);
const dialogImageUrl = ref('');

const openDialog = (url) => {
  dialogImageUrl.value = url;
  dialog.value = true;
};
</script>
