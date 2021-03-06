<template>
    <div v-if="user.role === 'MODERATOR' || user.role === 'ADMIN'">
        <div v-if="!show_preview" class="basic-block moderator-block">
            <label for="task_name">Название задания</label>
            <div>
                <input required type="text" id="task_name" v-model="request_body.task_name">
            </div>
            <div>
                <select required v-model="request_body.task_type">
                    <option disabled value="">Тип задания</option>
                    <option :value="type_enum.MAIN">Главное</option>
                    <option :value="type_enum.PHOTO">Фотозадание</option>
                    <option :value="type_enum.LOGIC">Логика</option>
                    <option :value="type_enum.DRAFT">Черновик</option>
                </select>
            </div>
            <label for="points">Количество очков</label>
            <div>
                <input type="number" id="points" v-model.number="request_body.points">
            </div>
            <label for="duration">Длительность (в минутах)</label>
            <div>
                <input type="number" id="duration" v-model.number="request_body.duration">
            </div>
            <label for="capacity">Пропускная способность</label>
            <div>
                <input type="number" id="capacity" v-model.number="request_body.capacity">
            </div>
            <label for="answers">Ответы</label>
            <div>
                <div>
                    <input required type="text" id="answers" v-model.trim="answer">
                </div>
                <div><span v-for="answer of request_body.answers" class="answer">{{answer}}, </span></div>
                <button class="moderator_btn" @click="request_body.answers = []; answer = ''">Очистить ответы</button>
                <button class="moderator_btn" @click="push_answer">Добавить ответ</button>
            </div>
            <vue-editor id="editor"
                        :editorToolbar="customToolbar"
                        useCustomImageHandler
                        @image-added="handleImageAdded"
                        v-model="request_body.html">
            </vue-editor>
            <button class="moderator_btn" v-if="this.$route.params.task_id" @click="update_task">Обновить</button>
            <button class="moderator_btn red-button" v-if="this.$route.params.task_id" @click="check_delete_task">Удалить задание</button>
            <button class="moderator_btn" v-else @click="send_task">Сохранить</button>
            <button class="moderator_btn" @click="show_preview = !show_preview">Предпросмотр</button>
            <button class="moderator_btn" @click="$router.push('/moderator/all_tasks')">Назад</button>
        </div>
        <div v-if="show_preview">
            <div class="preview basic-block"><h1 v-html="request_body.task_name"></h1>
                <div class="ql-editor" v-html="request_body.html"></div>
            </div>
            <button class="edit_btn" @click="show_preview = !show_preview">Редактировать</button>
        </div>
    </div>
</template>

<script>
    import Axios from "axios";
    import {VueEditor} from "vue2-editor";
    import {ErrorHandler} from "../../ErrorHandler";

    export default {
        name: 'TaskEditor',
        components: {
            VueEditor
        },
        data() {
            return {
                request_body: {
                    task_id: null,
                    task_name: "",
                    task_type: '',
                    points: 1,
                    duration: null,
                    capacity: 1,
                    html: "",
                    answers: [],
                    img_path: ""
                },
                type_enum: {
                    PHOTO: "PHOTO",
                    LOGIC: "LOGIC",
                    MAIN: "MAIN",
                    DRAFT: "DRAFT",
                },
                customToolbar: [[{'header': [1, 2, 3, 4, 5, 6, false]}],
                    ["bold", "italic", "underline", "strike"],
                    ["blockquote"],
                    ["link"],
                    [{align: ''}, {align: 'center'}, {align: 'right'}, {align: 'justify'}],
                    [{list: "ordered"}, {list: "bullet"}, {list: "check"}],
                    [{color: ["black", "white", "green", "blue", "purple", "yellow", "#f8e0be","#f8e0be", "#e1bf92", "#5f3e3b", "#d66363", "#32203a"]},],
                    ["image", "code-block"],],
                answer: "",
                show_preview: false
            };
        },
        mounted() {
            if (this.$route.params.task_id) {
                this.request_task_info()
            } else {
                this.get_task_id()
            }
        },
        computed: {
            user() {
                return this.$store.state.user
            }
        },
        beforeDestroy() {
            if(this.$store.state.error.message !== null)
                this.$store.commit('deleteErrorMessage')
        },
        methods: {
            check_delete_task(){
                let popup_options = {
                    message: 'Вы действительно хотите удалить задание?',
                    show: true,
                    callback: this.delete_task,
                    args: this.$route.params.task_id
                };
                this.$store.commit('deleteErrorMessage');
                this.$store.commit('setPopupOptions', popup_options)
            },
            delete_task(task_id) {
                Axios
                    .delete('task', {
                        params: {
                            task_id: task_id
                        }
                    })
                    .then(() => {
                        this.$router.push('/moderator')
                    })
                    .catch(error => {
                        if(error.response) {
                            new ErrorHandler(error.response, this)
                        } else {
                            this.$router.push('connection_error')
                        }
                    });
            },
            get_task_id() {
                Axios
                    .get('/task/all')
                    .then(response => {
                        let tasks = response.data;
                        if (tasks.length === 0){
                            this.request_body.task_id = 1;
                        }
                        tasks.sort(function (a, b) {
                            if (a.task_id > b.task_id) {
                                return -1;
                            }
                            if (a.task_id < b.task_id) {
                                return 1;
                            }
                            return 0;
                        });
                        this.request_body.task_id = tasks[0].task_id + 1
                    })
            },
            handleImageAdded: function (file, Editor, cursorLocation, resetUploader) {
                var formData = new FormData();
                formData.append("image", file);
                Axios
                    .post('/task/image', formData)
                    .then(result => {
                        this.request_body.img_path = Axios.defaults.baseURL + result.data;
                        Editor.insertEmbed(cursorLocation, "image", this.request_body.img_path);
                        resetUploader();
                    })
                    .catch(error => {
                        if(error.response) {
                            new ErrorHandler(error.response, this)
                        } else {
                            this.$router.push('connection_error')
                        }
                    });
            },
            request_task_info() {
                Axios
                    .get('/task/', {
                        params: {
                            task_id: this.$route.params.task_id
                        }
                    })
                    .then(response => {
                        this.request_body = response.data;
                    })
                    .catch(error => {
                        if(error.response) {
                            new ErrorHandler(error.response, this)
                        } else {
                            this.$router.push('connection_error')
                        }
                    });
            },
            push_answer() {
                if (this.answer === '') {
                    this.$store.commit('setErrorMessage', {
                        header: "Ошибка",
                        message: "Нельзя ввести пустой ответ."
                    });
                    return
                }
                this.request_body.answers.push(this.answer);
                this.answer = ""
            },
            send_task() {
                if (this.valid()) {
                    Axios
                        .post('/task', this.request_body)
                        .then(() => {
                            this.$router.push({
                                name: 'edit_task', params: {
                                    task_id: this.request_body.task_id
                                }
                            })
                        })
                        .catch(error => {
                            if(error.response) {
                                new ErrorHandler(error.response, this)
                            } else {
                                this.$router.push('connection_error')
                            }
                        });
                }
            },
            update_task() {
                if (this.valid()) {
                    Axios.put('/task', this.request_body)
                        .then(() => {
                            this.$store.commit('deleteErrorMessage')
                        })
                        .catch(error => {
                            if(error.response) {
                                new ErrorHandler(error.response, this)
                            } else {
                                this.$router.push('connection_error')
                            }
                        });
                }
            },
            valid() {
                if (this.request_body.task_type === '') {
                    this.$store.commit('setErrorMessage', {
                        header: "Ошибка",
                        message: "Определите тип задания."
                    });
                    return false
                }
                if ((this.request_body.duration > 1000)) {
                    this.$store.commit('setErrorMessage', {
                        header: "Ошибка",
                        message: "Значение числа в поле Продолжительность слишком большое."
                    });
                    return false
                }
                if ((this.request_body.points > 1000)) {
                    this.$store.commit('setErrorMessage', {
                        header: "Ошибка",
                        message: "Значение числа в поле Количество очков слишком большое."
                    });
                    return false
                }
                if ((this.request_body.capacity > 1000)) {
                    this.$store.commit('setErrorMessage', {
                        header: "Ошибка",
                        message: "Значение числа в поле Пропускная способность слишком большое."
                    });
                    return false
                }
                this.$store.commit('deleteErrorMessage');
                return true
            }
        }
    };
</script>

<style>
    .moderator_btn {
        margin: 10px;
    }

    .edit_btn {
        margin: 15px;
        background-color: #e1bf92;
    }
    .quillWrapper {
        background-color: white;
    }

    .ql-editor img {
        width: 100%;
        height: 100%;
    }

    .answer {
        color: black;
    }
</style>