package com.kabil.gazyava;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;

public final class MainActivity extends Activity {
    private WebView game;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        game = new WebView(this);
        game.setBackgroundColor(0xff2b1b4a);
        game.getSettings().setJavaScriptEnabled(true);
        game.getSettings().setDomStorageEnabled(true);
        game.getSettings().setAllowFileAccess(true);
        game.getSettings().setMediaPlaybackRequiresUserGesture(true);
        game.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !request.getUrl().toString().startsWith("file:///android_asset/");
            }
        });
        setContentView(game);
        game.loadUrl("file:///android_asset/index.html");
    }
    @Override protected void onPause() { super.onPause(); if (game != null) game.onPause(); }
    @Override protected void onResume() { super.onResume(); if (game != null) game.onResume(); }
    @Override protected void onDestroy() { if (game != null) game.destroy(); super.onDestroy(); }
}
