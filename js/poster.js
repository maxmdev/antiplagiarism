function posttext() {
    var formdata = new FormData();
    var xhr = new XMLHttpRequest();
    var select = $("option:selected").val();
    var text = $("#query").val();

    var union = $("#union").is(":checked");
    var pretext = $("#pretext").is(":checked");
    if (pretext == true) {
        formdata.append("stop-pretext", "checked")
    }
    if (union == true) {
        formdata.append("stop-union", "checked")
    }
    console.log(union + " " + pretext);
    console.log(select);
    console.log(text);
    formdata.append("select", select);
    formdata.append("query", text);
    var resp = "";
    console.log("DATA_SEND" + formdata);
    xhr.open("POST", "/", true);
    xhr.responseType = 'json'
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(resp);
            var specialChars = "!@#$^&%*()+=-[]\/\"\'{}|:<>?,.";
            stringToReplace = this.response;
            var resp = JSON.parse(stringToReplace.toString());
            console.log(resp);
            console.log(resp.filepath_input);
            $(".percent").text(resp.output);
            console.log(resp.filename);
            if (resp.filename === "") {
                $(".file").text("Збігів з файлами бази не знайдено.");
            } else {
                $(".file").text("Більшість збігів з файлом: " + resp.filename + ".");
            }
        }
    }
    xhr.send(formdata);
}