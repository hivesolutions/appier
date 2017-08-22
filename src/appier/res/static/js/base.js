var load = function() {
    if (document.querySelectorAll === undefined) {
        return;
    }

    var elements = document.querySelectorAll(".line.opener");
    for (var index = 0; index < elements.length; index++) {
        var element = elements[index];
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
    }

    highlightAll(".lines-extra");
};

var highlightAll = function(selector) {
    var targets = document.querySelectorAll(selector);
    for (var index = 0; index < targets.length; index++) {
        var target = targets[index];
        var elements = target.querySelectorAll(".line > .text");
        var raw = target.querySelector(".raw");
        raw = raw ? raw.textContent : null;
        var start = parseInt(target.getAttribute("data-start"));
        var end = parseInt(target.getAttribute("data-end"));
        var range = [start, end];
        highlightLibraries(elements, raw, range);
    }
};

var highlightLibraries = function(elements, raw, range) {
    highlightPrism(elements, raw, range);
    highlightHighlightJS(elements, raw, range);
};

var highlightPrism = function(elements, raw, range, language) {
    if (window.Prism === undefined) {
        return;
    }

    if (elements.length === 0) {
        return;
    }

    language = language || Prism.languages.python;

    var isRaw = raw ? true : false;

    if (isRaw) {
        var codeS = raw;
    } else {
        var codeBuffer = [];
        for (var index = 0; index < elements.length; index++) {
            var element = elements[index];
            var textS = element.textContent;
            codeBuffer.push(textS);
        }
        var codeS = codeBuffer.join("\n");
    }

    var tokens = Prism.tokenize(codeS, language);

    var partsBuffer = [];

    for (var index = 0; index < tokens.length; index++) {
        var token = tokens[index];
        var isString = typeof token === "string";
        var tokenContent = isString ? token : token.content;
        var tokenType = isString ? null : token.type;
        var tokenAlias = isString ? null : token.alias;
        var tokenClass = isString ? "" : "token ";
        tokenClass += token.type ? token.type + " " : "";
        tokenClass += token.alias ? token.alias + " " : "";

        var tokenParts = tokenContent.split("\n");
        for (var _index = 0; _index < tokenParts.length; _index++) {
            var tokenPart = tokenParts[_index];
            var isFirst = _index === 0;
            tokenPart = escapeHtml(tokenPart);
            var partS = (isFirst ? "" : "\n") + "<span class=\"" + tokenClass + "\"\>" + tokenPart + "</span>";
            partsBuffer.push(partS);
        }
    }

    var partsS = partsBuffer.join("");
    var parts = partsS.split("\n");

    parts = isRaw ? parts.slice(range[0], range[1]) : parts;

    for (var index = 0; index < parts.length; index++) {
        var part = parts[index];
        var element = elements[index];
        element.innerHTML = part;
    }
};

var highlightHighlightJS = function(elements, raw, range, language) {
    if (window.hljs === undefined) {
        return;
    }

    if (elements.length === 0) {
        return;
    }

    language = language || "python";

    var isRaw = raw ? true : false;

    if (isRaw) {
        var codeS = raw;
    } else {
        var codeBuffer = [];
        for (var index = 0; index < elements.length; index++) {
            var element = elements[index];
            var textS = element.textContent;
            codeBuffer.push(textS);
        }
        var codeS = codeBuffer.join("\n");
    }

    var highlighted = hljs.highlight(language, codeS);

    var partsS = highlighted.value;
    var parts = partsS.split("\n")

    parts = isRaw ? parts.slice(range[0], range[1]) : parts;

    for (var index = 0; index < parts.length; index++) {
        var part = parts[index];
        var element = elements[index];
        var invalid = part.indexOf("<span") !== -1 && part.indexOf("</span>") === -1;
        part += invalid ? "</span>" : "";
        element.innerHTML = part;
    }
};

var escapeHtml = function(unsafe) {
    safe = unsafe.replace(/&/g, "&amp;");
    safe = safe.replace(/</g, "&lt;");
    safe = safe.replace(/>/g, "&gt;");
    safe = safe.replace(/"/g, "&quot;");
    safe = safe.replace(/'/g, "&#039;");
    return safe;
};

window.addEventListener !== undefined && window.addEventListener("load", function() {
    load();
});
