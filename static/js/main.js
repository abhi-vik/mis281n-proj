dom = {};

POINTS_TO_CARD = 10000;

function reset() {
    dom.$giftsContainer.hide();
    dom.$giftsContainer.empty();
}

function makeUsernameSelect(usernames) {
    let selectSring = `<select class="form-control">`;
    usernames.sort().forEach((username) => {
        selectSring += `<option value=${username}>${username}</option>`;
    });
    selectSring += `</select>`;
    return $(selectSring);
}

function makeBalanceInput(max) {
    return $(`<input class="form-control" type="number" min="1" max="${max}"/>`);
}

function addSuccess($appendTo) {
    $('<div style="color: green">Done!</div>')
        .appendTo($appendTo)
        .fadeOut(1000, function () {
            $(this).remove()
        });
}

function renderGifts({user, usernames}, success) {
    const {giftable, redeemable} = user;

    dom.$giftsContainer.show();
    dom.$giftsContainer.append(`<p>You have ${giftable.balance} points left to give this month!</p>`);

    if (giftable.balance >= 1) {
        let receiver = null;
        let giftAmount = null;
        let message = "Thank you!";

        const $giftButton = $('<button class="btn btn-info" disabled>Gift</button>').click(() => {
            $.post({
                contentType: 'application/json',
                url: `/gift`,
                dataType: 'json',
                data: JSON.stringify({
                    receiver_username: receiver,
                    amount: giftAmount,
                    message: message
                })
            })
                .done(fetchDetails.bind(null, true));
        });

        function giftDisableCheck() {
            $giftButton.prop("disabled", !(receiver && giftAmount > 0 && giftAmount <= giftable.balance))
        }

        const $receiver = makeUsernameSelect(usernames).change(function () {
            receiver = $(this).val();
            giftDisableCheck()
        })
            .trigger("change");

        // dom.$giftsContainer.append(`<p>Your giftable balance: ${giftable.balance}</p>`);
        const $giftableAmount = makeBalanceInput(1000)
            .change(function () {
                giftAmount = parseInt($(this).val(), 10);
                giftDisableCheck()
            })
            .val(1)
            .trigger("change");

        const $messageInput = $(`<input class="form-control" placeholder="Thank you!"/>`).change(function () {
            message = $(this).val();
        });

        const $localContainer = $(`<div class="form-inline"></div>`);
        $localContainer.append($giftButton);
        $localContainer.append("&nbsp;");
        $localContainer.append($receiver);
        $localContainer.append("&nbsp;");
        $localContainer.append($giftableAmount);
        $localContainer.append("&nbsp;");
        $localContainer.append(" points, saying ");
        $localContainer.append("&nbsp;");
        $localContainer.append($messageInput);
        $localContainer.append("&nbsp;");
        dom.$giftsContainer.append($localContainer);
    }

    dom.$giftsContainer.append(`</br>`);
    dom.$giftsContainer.append(`<p>Your admirers have gifted you ${redeemable.balance} points!</p>`);

    if (redeemable.balance >= POINTS_TO_CARD) {
        let redeemCards = null;

        const $redeemButton = $('<button class="btn btn-info" disabled>Redeem</button>').click(() => {
            $.post({
                contentType: 'application/json',
                url: `/redeem`,
                dataType: 'json',
                data: JSON.stringify({
                    cards: redeemCards
                })
            })
                .done(fetchDetails.bind(null, true));
        });

        const $deduct = $(`<input class="form-control" readonly/>`);
        const $reward = $(`<input class="form-control" readonly/>`);
        const maxRedeem = Math.floor(redeemable.balance / POINTS_TO_CARD);
        const $redeemableInput = makeBalanceInput(maxRedeem)
            .change(function () {
                redeemCards = parseInt($(this).val(), 10);
                let enable = redeemCards > 0 && redeemCards <= maxRedeem;
                $redeemButton.prop("disabled", !enable);
                if (enable) {
                    $deduct.val('' + redeemCards * POINTS_TO_CARD);
                    $reward.val('$' + redeemCards * 100);
                }
            })
            .val(1)
            .trigger("change");

        const $localContainer = $(`<div class="form-inline"></div>`);
        $localContainer.append($redeemButton);
        $localContainer.append("&nbsp;");
        $localContainer.append($redeemableInput);
        $localContainer.append("&nbsp;cards or&nbsp;");
        $localContainer.append($deduct);
        $localContainer.append("&nbsp;points for&nbsp;");
        $localContainer.append($reward);
        dom.$giftsContainer.append($localContainer);

    } else {
        dom.$giftsContainer.append(`<p>${POINTS_TO_CARD - redeemable.balance} more till you can redeem them.</p>`);
    }

    if (success) {
        dom.$giftsContainer.append(`<br/>`);
        addSuccess(dom.$giftsContainer);
    }
}

function fetchDetails(success) {
    $.get({
        contentType: 'application/json',
        url: '/details',
        dataType: 'json'
    })
        .done((response) => {
            reset();
            if (_.isObject(response)) {
                renderGifts(response, success);
            } else {
                window.alert('Illegal state.');
            }
        });
}

window.onload = () => {
    dom.$giftsContainer = $('#gifts-container');

    fetchDetails(false)
};