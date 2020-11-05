function del() {
    let title = document.getElementById("event-title");
    if (title.innerHTML == "") {
        title.removeAttribute("required");
    }
}
