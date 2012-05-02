//Helper functions
var exports = module.exports;

exports.renderError = function(response, message) {
  response.render("error.ejs", {
    locals: {
      title: message ? message : "Error"
    }
  });
};