/**
 * Created with PyCharm.
 * User: tmehta
 * Date: 06/11/13
 * Time: 9:24 AM
 * To change this template use File | Settings | File Templates.
 */
interval = setInterval(function () {
    if ($('#paymentNumber')[0]) {
        $('#paymentNumber').val('4242 4242 4242 4242');
        $('#paymentExpiry').val('10 / 16');
        $('#paymentName').val('Doe');
        $('#paymentCVC').val('111');
        clearInterval(interval);
    }
}, 1000);
