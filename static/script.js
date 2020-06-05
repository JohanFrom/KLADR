/**
 * @author Johan From, Alva Karlborg, Laura Barba, Rebecka Persson
 */

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

$('#remove-form').submit(function () {
    var c = confirm("Vill du verkligen ta bort det här?");
    return c; //you can just return c because it will be true or false
});

function toggle(ID) {
    var element = document.getElementById(ID);
    if (element.style.display === "none" || element.style.display === "") {
        if (ID == "filter-menu" ) {
            element.style.display = "flex";
        } 
        else {
            element.style.display = "block";
        }
    } else {
        element.style.display = "none";
    }
}



setTimeout(function () {
    $('#success-message').fadeOut('fast');
}, 3000); // <-- time in milliseconds

