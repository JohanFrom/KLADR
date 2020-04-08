$(document).ready(function () {
    /*
        Döljer alla element (utom "<header>") i alla element av typen
        "<article>" med klassen "foldable"
    */
    $("article.foldable > *:not(header)").hide();

    $("article.foldable header").on("click", function () {
        $(this).nextAll("*").slideToggle();
    });
});

//Get the button:
mybutton = document.getElementById("my_btn");

window.onscroll = function () { scrollFunction() };

function scrollFunction() {
    if (document.body.scrollTop > 280 || document.documentElement.scrollTop > 280) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
}

function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

//function popUpFunction() {
    //myWindow = window.open("https://www.makemesmile.se/guider/kl%C3%A4dv%C3%A5rd-28064305", "", "width=1100, height=800");
//}





