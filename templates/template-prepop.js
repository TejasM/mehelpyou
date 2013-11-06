/**
 * Created with PyCharm.
 * User: tmehta
 * Date: 06/11/13
 * Time: 9:24 AM
 * To change this template use File | Settings | File Templates.
 */
interval = setInterval(function () {
    var f=$('.stripe-app');
    if (f.contents().find('#paymentNumber')[0]) {
        f.contents().find('#paymentNumber').val('4242 4242 4242 4242');
        f.contents().find('#paymentExpiry').val('10 / 16');
        f.contents().find('#paymentName').val('Doe');
        f.contents().find('#paymentCVC').val('111');
        clearInterval(interval);
    }
}, 1000);
