import pynotify;

pynotify.init("Hello world");

n = pynotify.Notification("Test", "Testing some shit yo");
n.show();
