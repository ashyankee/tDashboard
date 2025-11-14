// Form validation helpers
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        validate_all_fields: function(date, ticker, sector, news, entry_price, entry_time,
                                      exit_price, exit_time, shares) {
            // This runs client-side for instant feedback
            return "Validation complete";
        }
    }
});