/**
 * JavaScript 代码质量问题示例
 */

// 问题1: 使用 var 而不是 const/let
function processUserList(users) {
    var result = "";
    for (var i = 0; i < users.length; i++) {
        result += users[i].name + " - " + users[i].email + "\n";
    }
    return result;
}

// 问题2: 回调地狱 (Callback Hell)
function fetchUserData(userId, callback) {
    fetchUser(userId, function(err, user) {
        if (err) {
            fetchUserProfile(user.id, function(err, profile) {
                if (err) {
                    fetchUserSettings(profile.id, function(err, settings) {
                        if (err) {
                            callback(null, { user, profile, settings });
                        } else {
                            callback(err);
                        }
                    });
                } else {
                    callback(err);
                }
            });
        } else {
            callback(err);
        }
    });
}

// 问题3: 全局变量污染
globalCounter = 0;
function incrementCounter() {
    globalCounter++;
    return globalCounter;
}

// 问题4: 没有错误处理的异步操作
async function loadDataWithoutErrorHandling() {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    return data;
}

// 问题5: 行过长
function complexCalculation(a, b, c, d, e, f) { return (a * b + c * d - e * f) / (a + b + c + d + e + f) * Math.sqrt(a * b * c * d * e * f); }

// 问题6: 使用 eval
function evaluateExpression(expr) {
    return eval(expr);
}

// 问题7: 嵌套过深
function processNestedData(data) {
    if (data) {
        if (data.users) {
            if (Array.isArray(data.users)) {
                if (data.users.length > 0) {
                    if (data.users[0].profile) {
                        if (data.users[0].profile.settings) {
                            return data.users[0].profile.settings;
                        }
                    }
                }
            }
        }
    }
    return null;
}
