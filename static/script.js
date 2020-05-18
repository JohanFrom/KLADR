//SCROLL UP
$(document).ready(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() > 800) {
            $('#scroll').fadeIn();
        }
        else {
            $('#scroll').fadeOut();
        }
    });

    $('#scroll').click(function () {
        $("html, body").animate(
            { scrollTop: 0 }, 700);
        return false;
    });
});

$('#remove-form').submit(function() {
    var c = confirm("Vill du verkligen ta bort det här?");
    return c; //you can just return c because it will be true or false
});
// $(document).ready(function () {
//     /*
//         Döljer alla element (utom "<header>") i alla element av typen
//         "<article>" med klassen "foldable"
//     */
//     $("article.foldable > *:not(header)").hide();

//     $("article.foldable header").on("click", function () {
//         $(this).nextAll("*").slideToggle();
//     });
// });

function toggle(ID) {
    var element = document.getElementById(ID);
    if (element.style.display === "none" || element.style.display === "") {
        if (ID == "filter-menu") {
            element.style.display = "flex";
        } else {
            element.style.display = "block";
        }
    } else {
        element.style.display = "none";
    }
}
// //Get the button:
// mybutton = document.getElementById("my_btn");

// window.onscroll = function () { scrollFunction() };

// function scrollFunction() {
//     if (document.body.scrollTop > 280 || document.documentElement.scrollTop > 280) {
//         mybutton.style.display = "block";
//     } else {
//         mybutton.style.display = "none";
//     }
// }

// function topFunction() {
//     document.body.scrollTop = 0;
//     document.documentElement.scrollTop = 0;
// }

setTimeout(function () {
    $('#success-message').fadeOut('fast');
}, 3000); // <-- time in milliseconds


//$(window).click(function(){$('.messages.status').fadeOut();});

//function popUpFunction() {
    //myWindow = window.open("https://www.makemesmile.se/guider/kl%C3%A4dv%C3%A5rd-28064305", "", "width=1100, height=800");
//}

//Form validation
