{
    // creating variables
    createUser = true;
    onLoad();
    //to load the users on loading of the script
    function onLoad() {
        $.ajax({
            type: "get",
            url: "/admin/users/fetch/",
            success: function (response) {
                setTheme("users")
                renderUsers(response.users);
            },
            error: function (error) {
                toastr.error("Unable to load users!");
            }
        });

    }

    //to render the users on the DOM
    function renderUsers(users) {
        $(".main-container").html("");
        users.forEach(user => {
            let itemContainer = $("<div>").addClass("user-container").attr("id", `user--${user.id}`);
            let name = $("<p>").attr("id", `user--${user.id}`).text(user.name);
            let deleteBtn = $("<img>").attr({ "id": user.id, "src": "/static/images/icons/delete.png", "class": "delete-user" });
            itemContainer.append(name, deleteBtn);
            $(".main-container").prepend(itemContainer);
        });
        addBtn = $("<div>").addClass("add-btn").attr({ "id": "add-user", "src": "/static/images/icons/add.png" });
        addBtnText = $("<p>").text("ADD USER");
        addBtn.append(addBtnText);
        $(".main-container").append(addBtn);

    }

    // to convert the price into currency format
    function formatPrice(price) {
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR"
        }).format(price).replace(".00", "");
    }


    // to render the listing
    function renderListings(response) {
        $(".main-container").html("");
        if (!response.response) {
            toastr.error(response.error);
            return;
        }
        response.response.data.forEach(item => {
            let itemContainer = $("<div>").addClass("listing-container").attr("id", `listing--${item.id}`);
            let div = $("<div>");
            let title = $("<p>").text(item.title).addClass("item-title");
            let userStrong = $("<strong>").text(item.user);
            let user = $("<p>").text(`User: `).addClass("item-user");
            let categoryStrong = $("<strong>").text(item.category);
            let category = $("<p>").text(`Category: `).addClass("item-category");
            let deleteBtn = $("<img>").attr({ "id": item.id, "src": "/static/images/icons/delete.png", "class": "delete-listing" });
            let priceStrong = $("<strong>").text(formatPrice(item.price));
            let price = $("<p>").text(`Price: `).addClass("item-price");
            user.append(userStrong);
            category.append(categoryStrong);
            price.append(priceStrong);
            div.append(title, user, category, price);
            itemContainer.append(div, deleteBtn);
            $(".main-container").prepend(itemContainer);
        });

    }

    //to fetch the users
    function fetchUsers() {
        onLoad();
    }

    //to fetch the listings
    async function fetchListings() {
        try {
            let response = await fetch("/admin/listings/fetch/", {
                method: "get",
                headers: { "x-requested-with": "XMLHttpRequest" }
            });
            if (response.ok) return { response: await response.json(), error: null };
            return { response: null, error: "Unable to load Listings" };
        } catch (e) {
            return { response: null, error: "Unable to load Listings" };
        }
    }
    //to delete the the listing
    async function deleteListing(id) {
        try {
            let response = await fetch(`/admin/listings/destroy/${id}`, {
                method: "get",
                headers: { "x-requested-with": "XMLHttpRequest" }
            });
            if (response.ok) {
                data = await response.json();
                document.getElementById(`listing--${id}`).remove();
                toastr.success(data.message);
                return;
            }
            toastr.error("Something went wrong!");

        } catch (e) {
            toastr.error("Something went wrong!");
        }
    }

    //to set the menu icon theme
    function setTheme(set, remove) {
        $(`#${set}`).css("border", "1px solid var(--primaryColor)");
        $(`#${set}>div`).css("backgroundColor", "var(--primaryColor)");
        $(`#${set} img`).attr("src", `/static/images/icons/${set}_white.png`);

        //to remove the theme form items
        if (remove) {
            $(`#${remove}`).css("border", "none");
            $(`#${remove}>div`).css("backgroundColor", "white");
            $(`#${remove} img`).attr("src", `/static/images/icons/${remove}.png`);
        }
    }

    // ----------------EVENT HANDLERS---------------------

    //to add the user
    function addUserBtnClickHandler() {
        window.location.href = "/admin/users/create/";
    }

    function userItemClickHandler(event) {
        let id = event.target.id;
        window.location.href = `/admin/users/${id.split("--")[1]}`;
    }

    function onDeleteUserBtnClickHandler(event) {
        event.stopPropagation();
        event.preventDefault();
        $(".delete-popup-container").css("display", "flex");
        $(".option-yes").attr("id", event.target.id);
    }
    function onNoClickHandler() {
        $(".delete-popup-container").css("display", "none");
    }


    function onYesClickHandler(event) {
        let id = event.target.id;
        $(".delete-popup-container").css("display", "none");
        $.ajax({
            type: "get",
            url: `/admin/users/destroy/${id}`,
            success: function (response) {
                document.getElementById(`user--${id}`).remove();
                toastr.success(response.message);
            },
            error: (error) => {
                toastr.error(error.responseJSON.message);
            }
        });

    }


    async function listingBtnClickHandler() {
        setTheme("listings", "users")
        response = await fetchListings();
        renderListings(await fetchListings());
    }


    function userBtnClickHandler() {
        setTheme("users", "listings")
        fetchUsers();
    }



    function deleteListingBtnClickHandler(event) {
        deleteListing(event.target.id);
    }

    // ----------------EVENT LISTENERS---------------------
    $(".main-container").on("click", "#add-user", addUserBtnClickHandler);
    $(".main-container").on("click", ".user-container", userItemClickHandler);
    $(".main-container").on("click", ".delete-user", onDeleteUserBtnClickHandler);
    $(".delete-popup>img").click(onNoClickHandler);
    $(".option-yes").click(onYesClickHandler);
    $(".option-no").click(onNoClickHandler);
    $(".main-container").on("click", ".delete-listing", deleteListingBtnClickHandler);
    $("#listings").on("click", listingBtnClickHandler);
    $("#users").on("click", userBtnClickHandler);

}