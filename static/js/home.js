{
    // calling onload function
    let previousSelected="all";
    onLoad();


    async function onLoad() {
        fetchItems();
        setStyle("all")
    }

    // to fetch the items form the server
    async function fetchItems() {
        let response = await fetch(`/api/listings/fetch/?all=True`);
        let data = await response.json();
        renderItems(data.data)

    }

    // to convert the price into currency format
    function formatPrice(price){
        return new Intl.NumberFormat("en-IN",{
            style:"currency",
            currency:"INR"
        }).format(price).replace(".00","");
    }

    // to render the items on DOM
    function renderItems(data) {
        $(".items-container").html("");
        data.forEach(item => {
            let div = $("<div>").addClass("item-container on-listing-hover").attr("id", item.id);
            let img = $("<img>").attr("id", item.id).addClass("image-hover");
            if (item.images[0]) img.attr("src", item.images[0].image);
            else img.attr("src", "static/images/icons/image.png");
            let title = $("<p>").addClass("title").text(item.title).attr("id", item.id);
            let price = $("<p>").addClass("price").text(formatPrice(item.price)).attr("id", item.id);
            div.append(img, title, price);
            $(".items-container").prepend(div);
        });
    }

    //to the the item according to query and filter
    async function fetchItemsQuery(query, filter) {
        let data;
        if (filter) {
            if(query==="all") {
                onLoad(); return;
            }
            let response = await fetch(`/api/listings/filter/?query=${query}`);
            data = await response.json();
        } else {
            let response = await fetch(`/api/listings/search/?query=${query}`);
            data = await response.json();
        }
        renderItems(data.data);
    }

    function setStyle(category){
        $(`#${previousSelected}`).css({border:"none",backgroundColor:"rgba(0,0,0,0)",color:"var(--primaryColor)", "fontWeight":"400"});
        $(`#${category}`).css({border:"2px solid var(--primaryColor)",backgroundColor:"var(--primaryColor)",color:"white", "fontWeight":"800"});
        previousSelected=category;
    }

    // --------------EVENT HANDLERS----------------

    function itemClickHandler(event) {
        let id = event.target.id;
        if (id) window.location.href = `/listings/fetch/${id}`;
    }

    function categoriesClickHandler(event) {
        let query = $(event.target).attr("value");
        setStyle(event.target.id);
        fetchItemsQuery(query, true);
    }

    function onSearchInputFocusHandler() {
        $(".inner-div").css({ "border": "2px solid var(--buttonColor)", "background-color": "var(--primaryColor)" });
    }

    function onSearchInputBlurHandler() {
        $(".inner-div").css({ "border": "2px solid var(--borderColor)", "background-color": "var(--borderColor)" });
    }

    function searchInputEnterPressHandler(event) {
        if(event.key!=="Enter") return;
        let val = event.target.value;
        if (!val) fetchItems()
        else fetchItemsQuery(val);
    }

    function searchBtnClickHandler() {
        fetchItemsQuery($(".item-search").val());
    }


    // --------------EVENT LISTENERS----------------
    $(".categories>li").each((index, item) => {
        $(item).click(categoriesClickHandler);
    });
    $(".items-container").on("click", ".item-container", itemClickHandler);
    $(".item-search").on("keypress", searchInputEnterPressHandler);
    $(".search-icon").click(searchBtnClickHandler);
}