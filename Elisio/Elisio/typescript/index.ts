import Vue from 'vue'

window.onload = function() {
    let app = new Vue({
        delimiters: ['[[',']]'],
        el: '#app',
        data: {
            message: "the bees made honey in the lion's skull"
        }
    });
};
