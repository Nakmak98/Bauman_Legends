<template>
    <div id="app">
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
                <span class="push-answer" @click="push_answer">+</span>
            </div>
            <div><span v-for="answer of request_body.answers">{{answer}}, </span></div>
            <span class="clear-answers" @click="request_body.answers = []; answer = ''">Очистить ответы</span>
        </div>
        <vue-editor id="editor"
                    :editorToolbar="customToolbar"
                    useCustomImageHandler
                    @image-added="handleImageAdded"
                    v-model="request_body.html">
        </vue-editor>
        <button v-if="this.$route.params.task_id" @click="update_task">Обновить</button>
        <button v-if="this.$route.params.task_id" @click="delete_task">Удалить задание</button>
        <button v-else @click="send_task">Сохранить</button>
        <div class="preview" v-html="request_body.html"></div>
    </div>
</template>

<script>
    import {VueEditor} from "vue2-editor";
    import Axios from "axios";

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
                customToolbar: [[{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                                ["bold", "italic", "underline", "strike"],
                                ["blockquote"],
                                [{ align: '' }, { align: 'center' }, { align: 'right' }, { align: 'justify' }],
                                [{ list: "ordered" }, { list: "bullet" }, { list: "check" }],
                                [{ color: ["black", "white", "green", "blue", "purple", "yellow"] },],
                                ["image", "code-block"],  ],
                answer: ""
            };
        },
        mounted() {
            if (this.$route.params.task_id) {
                this.request_task_info()
            } else {
                this.get_task_id()
            }
        },
        methods: {
            delete_task() {
                Axios
                    .delete('task', {
                        params: {
                            task_id: this.$route.params.task_id
                        }
                    })
                    .then(() => {
                        this.$router.push('/moderator')
                    })
                    .catch(error => {
                        if (error.response) {
                            if (error.response.status === 401) {
                                this.$router.push('auth');
                                this.$store.commit('setErrorMessage', {
                                    header: "Ошибка авторизации",
                                    message: error.response.data.message
                                });
                            } else {
                                this.$store.commit('setErrorMessage', {
                                    header: "Ошибка",
                                    message: error.response.data.message
                                });
                            }

                        }
                    });
            },
            get_task_id() {
                Axios
                    .get('/task/all')
                    .then(response => {
                        let tasks = response.data;
                        tasks.sort(function (a, b) {
                            if (a.task_id > b.task_id) {
                                return -1;
                            }
                            if (a.task_id < b.task_id) {
                                return 1;
                            }
                            return 0;
                        });
                        console.log(tasks[0].task_id);
                        this.request_body.task_id = tasks[0].task_id + 1
                    });
            },
            handleImageAdded: function (file, Editor, cursorLocation, resetUploader) {
                console.log(file.name);
                var formData = new FormData();
                formData.append("image", file);
                Axios
                    .post('/task/image', formData)
                    .then(result => {
                        this.request_body.img_path = Axios.defaults.baseURL + result.data;
                        Editor.insertEmbed(cursorLocation, "image", this.request_body.img_path);
                        resetUploader();
                    })
                    .catch(err => {
                        console.log(err);
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
                    .catch(async error => {
                        // setErrorMessage выполнялся раньше push,
                        // что приводило к некорректной работе при уведомлении сообщений
                        // помог async/await
                        if (error.response) {
                            if (error.response.status === 401) {
                                await this.$router.push('/auth');
                                this.$store.commit('setErrorMessage', {
                                    header: "Ошибка авторизации",
                                    message: error.response.data.message
                                });
                            } else {
                                this.$store.commit('setErrorMessage', {
                                    header: "Ошибка",
                                    message: error.response.data.message
                                });
                            }
                        }
                    })
            },
            push_answer() {
                this.request_body.answers.push(this.answer);
                this.answer = ""
            },
            send_task() {
                if (this.valid()) {
                    Axios
                        .post('/task', this.request_body)
                        .then(() => {
                            this.$router.push({name: 'edit_task', params:{
                                task_id: this.request_body.task_id}
                            })
                        })
                        .catch(error => {
                            if (error.response) {
                                if (error.response.status === 401) {
                                    this.$router.push('/auth');
                                    this.$store.commit('setErrorMessage', {
                                        header: "Ошибка авторизации",
                                        message: error.response.data.message
                                    });
                                } else {
                                    this.$store.commit('setErrorMessage', {
                                        header: "Ошибка",
                                        message: error.response.data.message
                                    });
                                }

                            }
                        });
                }
            },
            update_task() {
                Axios.put('/task', this.request_body)
                    .then(() => {
                        this.$store.commit('deleteErrorMessage')
                    })
                    .catch(error => {
                        if (error.response) {
                            if (error.response.status === 401) {
                                this.$router.push('/auth');
                                this.$store.commit('setErrorMessage', {
                                    header: "Ошибка авторизации",
                                    message: error.response.data.message
                                });
                            } else {
                                this.$store.commit('setErrorMessage', {
                                    header: "Ошибка",
                                    message: error.response.data.message
                                });
                            }

                        }
                    });
            },
            valid() {
                if(this.request_body.task_type === ''){
                    this.$store.commit('setErrorMessage', {
                        header: "Ошибка",
                        message: "Определите тип задания"
                    });
                    return false
                }
                this.$store.commit('deleteErrorMessage')
                return true
            }
        }
    };
</script>

<style>
    span {
        cursor: pointer;
    }

    .push-answer {
        font-size: 25px;
        color: green;
    }

    .clear-answers {
        color: red;
    }
</style>