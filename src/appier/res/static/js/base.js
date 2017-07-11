var load = function() {
    if (document.querySelectorAll === undefined) {
        return;
    }

    var elements = document.querySelectorAll(".line.opener");
    elements.forEach(function(element) {
        element.addEventListener("click", function() {
            var targetId = this.getAttribute("data-id");
            var target = document.querySelector(".lines-extra[data-id=\"" + targetId + "\"]");
            var style = target.style;
            if (style.display === "block") {
                target.style.display = "none";
            } else {
                target.style.display = "block";
            }
        });
    });
}

window.addEventListener("load", function() {
    load();
});
