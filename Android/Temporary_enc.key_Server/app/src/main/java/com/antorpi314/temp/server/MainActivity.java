package com.antorpi314.temp.server;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.InputType;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.widget.*;
import android.app.Activity;

public class MainActivity extends Activity {
    EditText encKeyEditText;
    Button toggleServerButton, saveKeyButton;
    CheckBox showKeyCheckbox;
    boolean isServerRunning = false;

    private static final String PREF_NAME = "MyPrefs";
    private static final String KEY_ENC = "enc_key";
    private static final String KEY_SERVER_STATE = "server_running";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        encKeyEditText = findViewById(R.id.encKeyEditText);
        toggleServerButton = findViewById(R.id.toggleServerButton);
        showKeyCheckbox = findViewById(R.id.showKeyCheckbox);
        saveKeyButton = findViewById(R.id.saveKeyButton);

        SharedPreferences prefs = getSharedPreferences(PREF_NAME, MODE_PRIVATE);

        String savedKey = prefs.getString(KEY_ENC, "A000-000-000-000");
        encKeyEditText.setText(savedKey);

        isServerRunning = prefs.getBoolean(KEY_SERVER_STATE, false);
        updateToggleButton();

        showKeyCheckbox.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked)
                encKeyEditText.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD);
            else
                encKeyEditText.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
            encKeyEditText.setSelection(encKeyEditText.length());
        });

        saveKeyButton.setOnClickListener(v -> {
            String key = encKeyEditText.getText().toString().trim();
            SharedPreferences.Editor editor = prefs.edit();
            editor.putString(KEY_ENC, key);
            editor.apply();
            Toast.makeText(this, "Key saved successfully", Toast.LENGTH_SHORT).show();
        });

        toggleServerButton.setOnClickListener(v -> {
            SharedPreferences.Editor editor = prefs.edit();

            if (!isServerRunning) {
                String key = encKeyEditText.getText().toString();
                Intent i = new Intent(this, MyServerService.class);
                i.putExtra("key", key);

                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                    startForegroundService(i);
                } else {
                    startService(i);
                }

                isServerRunning = true;
                editor.putBoolean(KEY_SERVER_STATE, true);
            } else {
                stopService(new Intent(this, MyServerService.class));
                isServerRunning = false;
                editor.putBoolean(KEY_SERVER_STATE, false);
            }

            editor.apply();
            updateToggleButton();
        });
    }

    private void updateToggleButton() {
        if (isServerRunning) {
            toggleServerButton.setText("Stop Server");
            toggleServerButton.setBackgroundTintList(ColorStateList.valueOf(Color.parseColor("#dc3545"))); // Red
        } else {
            toggleServerButton.setText("Start Server");
            toggleServerButton.setBackgroundTintList(ColorStateList.valueOf(Color.parseColor("#28a745"))); // Green
        }
    }
}
