function (user, context, callback) {
    // Just a simple rule to assign scopes on the fly.
    // User john.gateley@gmail.com is an admin and can do anything
    // Everyone else can only read and write
    if (user.email === 'john.gateley@gmail.com') {
	context.accessToken.scope = ['openid', 'profile', 'email', 'read:data', 'write:data', 'delete:data'];
    } else {
	context.accessToken.scope = ['openid', 'profile', 'email', 'read:data', 'write:data'];
    }
    callback(null, user, context);
}
