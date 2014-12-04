// Copyright 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package com.google.android.apps.appspeedindex;

import android.app.Activity;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;

import java.lang.Runnable;

public class BoundingBox extends Activity {
    final Paint paint = new Paint();
    final Handler handler = new Handler();

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        paint.setStyle(Paint.Style.FILL);
        final View view = new View(this) {
          @Override
          public void onDraw(Canvas canvas) {
            canvas.drawRect(0, 0, getWidth(), getHeight(), paint);
          }
        };

        view.setLayoutParams(new ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.FILL_PARENT, ViewGroup.LayoutParams.FILL_PARENT));
        setContentView(view);

        paintDelayed(view, 0, 255, 0, 0);
        paintDelayed(view, 0, 0, 255, 640);

    }

    private void paintDelayed(
        final View view, final int r, final int g, final int b, long delay) {
        handler.postDelayed(new Runnable() {
          @Override
          public void run() {
            paint.setARGB(255, r, g, b);
            view.invalidate();
          }
        }, delay);
    }
}
