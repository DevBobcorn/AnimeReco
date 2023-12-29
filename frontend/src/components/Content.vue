<script setup>
import { ref } from 'vue'
import axios from "axios";

const server_url = ref('http://127.0.0.1:5003')

const uploadPreviewUrl = ref("")
const outputPreviewUrl = ref("")
const detectedList = ref([])
const waitMessage = ref("等待上传")
const loading = ref(false)
const showUpload = ref(true)
const dialogTableVisible = ref(false)

// Template refs
const upload = ref(null)
const reupload = ref(null)

function upload_click() {
  upload.value.click();
}

function reupload_click() {
  reupload.value.click();
}

// 获得目标文件
function getObjectURL(file) {
  var url = null;
  if (window.createObjcectURL != undefined) {
    url = window.createOjcectURL(file);
  } else if (window.URL != undefined) {
    url = window.URL.createObjectURL(file);
  } else if (window.webkitURL != undefined) {
    url = window.webkitURL.createObjectURL(file);
  }
  return url;
}

// 上传文件
function uploadImage(e) {
  dialogTableVisible.value = true;
  uploadPreviewUrl.value = "";
  outputPreviewUrl.value = "";

  waitMessage.value = "";
  detectedList.value = [];
  loading.value = true;
  showUpload.value = false;

  let file = e.target.files[0];
  uploadPreviewUrl.value = getObjectURL(file);

  let param = new FormData(); //创建form对象
  param.append("file", file, file.name); //通过append向form对象添加数据

  axios
    .post(server_url.value + "/upload", param, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((response) => {
      // Update image previews
      uploadPreviewUrl.value = server_url.value + '/' + response.data.upload_url;
      outputPreviewUrl.value = server_url.value + '/' + response.data.output_url;

      loading.value = false;

      let resultList = Object.keys(response.data.image_info);

      for (var i = 0; i < resultList.length; i++) {
        detectedList.value.push(response.data.image_info[resultList[i]]);
      }

      dialogTableVisible.value = false;
    });
}

</script>

<template>
  <div id="Content">
    <el-dialog title="YOLOv5处理中…" :visible.sync="dialogTableVisible" :show-close="false" :close-on-press-escape="false"
      :append-to-body="true" :close-on-click-modal="false" :center="true">
      <span slot="footer" class="dialog-footer">请稍候…</span>
    </el-dialog>

    <div id="container_image">
      <el-card id="container_image_card" class="preview_panel">
        <div class="preview_container">
          <div v-loading="loading" element-loading-text="上传图片中…">
            <el-image :src="uploadPreviewUrl" class="preview" :preview-src-list="[uploadPreviewUrl]"
              style="border-radius: 3px 3px 0 0">
              <template #error>
                <el-button v-show="showUpload" type="primary" v-on:click="upload_click">
                  Upload
                  <input ref="upload" style="display: none" name="file" type="file" @change="uploadImage" />
                </el-button>
              </template>
            </el-image>
          </div>
          <div class="preview_label">
            <span>Input</span>
          </div>
        </div>
        <div class="preview_container">
          <div v-loading="loading" element-loading-text="处理中，请稍候…">
            <el-image :src="outputPreviewUrl" class="preview" :preview-src-list="[outputPreviewUrl]"
              style="border-radius: 3px 3px 0 0">
              <template #error>
                <div slot="placeholder" class="error">{{ waitMessage }}</div>
              </template>
            </el-image>
          </div>
          <div class="preview_label">
            <span>Output</span>
          </div>
        </div>
      </el-card>
    </div>
    <div id="container_result">
      <!-- 卡片放置表格 -->
      <el-card style="border-radius: 8px;">
        <div slot="header" class="clearfix table_header">
          <span>结果列表：</span>
          <el-button style="margin-left: 35px" v-show="!showUpload" type="primary" v-on:click="reupload_click">
            重新选择图像
            <input ref="reupload" style="display: none" name="file" type="file" @change="uploadImage" />
          </el-button>
        </div>
        <el-table :data="detectedList" height="390" border v-loading="loading" element-loading-text="处理中，请稍候…" lazy>
          <!-- 0: width, 1: height, 2: best match label, 3: best match score, 4: preview image (base64 encoded uri) -->
          <el-table-column label="Preview" width="250px">
            <template #default="scope">
              <span>
                <img class="result_preview" :src="scope.row[4]">
              </span>
            </template>
          </el-table-column>
          <el-table-column label="Size" width="250px">
            <template #default="scope">
              <span>{{ scope.row[0] }} * {{ scope.row[1] }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Best Match" width="250px">
            <template #default="scope">
              <span>{{ scope.row[2] }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Score" width="250px">
            <template #default="scope">
              <span>{{ scope.row[3] }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
  <div style="clear: both;"></div>
</template>

<style>
.n1 .el-step__description {
  padding-right: 20%;
  font-size: 14px;
  line-height: 20px;
}

.el-image__inner {
  object-fit: contain;
}
</style>

<style scoped>
#Content {
  font-family: Arial, Helvetica, sans-serif;
  background-color: #ffffff;
  content: "";
  display: table;
  clear: both;
}

.dialog_info {
  margin: 20px auto;
}

.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}

.table_header {
  margin-bottom: 8px;
}

#container_image {
  width: 440px;
  float: left;
  padding: 1%;
}

#container_image_card {
  width: 100%;
  height: 40%;
  margin: 0px auto;
  padding: 0px auto;
  margin-right: 180px;
  margin-bottom: 0px;
  border-radius: 4px;
}

.preview_panel {
  border-radius: 8px;
  margin: 20px;
}

.preview_panel {
  border-radius: 8px;
  margin: 20px;
}

.preview_container {
  margin: 20px 20px;
  display: inline-block;
}

.preview {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 360px;
  height: 240px;
  background: #ffffff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.preview_label {
  height: 30px;
  text-align: center;
  background-color: rgba(255, 135, 195, 0.878);
  color: white;
  line-height: 30px;
  border-radius: 0 0 5px 5px
}

#container_result {
  width: calc(96% - 460px);
  height: 100%;
  float: left;
  padding: 1%;
}

.result_preview {
  max-height: 50px;
  width: auto;
}
</style>