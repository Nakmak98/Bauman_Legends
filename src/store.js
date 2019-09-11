import Vue from 'vue'
import Vuex from 'vuex'
import Axios from "axios";

Vue.use(Vuex)

let popup_default_options = {
    message: '',
    placeholder: '',
    input_field: false,
    show: false,
    callback: null,
    args: null
};

export default new Vuex.Store({
    state: {
        user: null,
        team: null,
        team_members: null,
        popup: popup_default_options
    },
    mutations: {
        setUserData(state, data) {
            state.user = data;
        },
        setTeamData(state, data) {
            state.team = data
        },
        setTeamMembers(state, data) {
            state.team_members = data
        },
        setPopupOptions(state, data) {
            state.popup = data
        },
        setPopupInputValue(state, data) {
            state.popup.value = data
        },

        deleteTeamMembers(state) {
            state.team_members = null;
        },

        deleteTeamData(state) {
            state.team = null;
        },
        deleteUserData(state) {
            state.user = null;
        },
        deletePopupOptions(state) {
            state.popup = popup_default_options
        }
    },
    getters: {
        getUserData: state => state.user,
        getTeamData: state => state.team
    },
    actions: {
        updateUserData(context) {
            Axios
                .get('/user/info')
                .then(response => {
                    console.log(response)
                    context.commit('setUserData', response.data)
                })
        },
        updateTeamMembers(context) {
            Axios
                .get('/team/members')
                .then(response => {
                    console.log(response.data);
                    context.commit('setTeamMembers', response.data);
                })
        }
    }
})
