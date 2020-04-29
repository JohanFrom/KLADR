//SCROLL UP
$(document).ready(function()
{
    $(window).scroll(function()
    {
        if ($(this).scrollTop() > 800)
        {
            $('#scroll').fadeIn();
        }
        else
        { $('#scroll').fadeOut();
        }
    });

    $('#scroll').click(function()
    {
        $("html, body").animate(
            {scrollTop: 0}, 700);
            return false;
    });
});


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
