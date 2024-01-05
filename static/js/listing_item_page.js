{
    // calling function on loading of the script
    onLoad();
    // declaring global variables
    let data;
    let imageIndex = 0;

    // onload function
    async function onLoad() {
        // getting the id of the item from the template
        let id = $(".get-id").attr("id");
        // fetching images relating to item
        let response = await fetch(`/listings/fetch/${id}`, {
            method: "get",
            headers: { "x-requested-with": "XMLHttpRequest" }
        });
        data = await response.json();
        renderImage(data);
    }
    // function to render the image on DOM
    function renderImage(data) {
        if (imageIndex > 0) $("#prev-btn").css("display", "block");
        if (imageIndex <= 0) $("#prev-btn").css("display", "none");
        if (imageIndex >= data.images.length - 1) $("#next-btn").css("display", "none");
        if (imageIndex < data.images.length - 1) $("#next-btn").css("display", "block");
        // if the images found
        if (data && data.images.length) {
            $("#carousel-image").attr("src", data.images[imageIndex].image);
            // if there is no image associated with the item
        } else {
            $("#carousel-image").attr({ "src": "/static/images/icons/add_image_white.png", "class": "add-image" })
                .css({ "height": "40vh", "margin": "20vh auto" });
            $("#next-btn").css("display", "none");
            $("#prev-btn").css("display", "none");
        }
    }

    // ------------------EVENT HANDLERS--------------------

    // next button click handler
    function nextBtnClickHandler() {
        imageIndex++;
        if (imageIndex >= data.images.length) { imageIndex--; return };
        renderImage(data);
    }
    // previous button click handler
    function prevBtnClickHandler() {
        imageIndex--;
        if (imageIndex < 0) { imageIndex++; return };
        renderImage(data);
    }

    // to mail the user if someone is interested in their product
    async function onNotifyUserClickHandler(event) {
        let response = await fetch(`/listings/${event.target.id}/notify-user/mail/`);
        let data = await response.json();
        if (response.ok) toastr.success(data.message);
        else toastr.error(data.message);
    }
    // ------------------EVENT LISTENERS--------------------

    $("#next-btn").click(nextBtnClickHandler);
    $("#prev-btn").click(prevBtnClickHandler);
    $(".notify-user").click(onNotifyUserClickHandler);
}
