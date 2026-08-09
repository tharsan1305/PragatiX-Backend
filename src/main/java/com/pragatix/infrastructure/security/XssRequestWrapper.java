package com.pragatix.infrastructure.security;

import jakarta.servlet.ReadListener;
import jakarta.servlet.ServletInputStream;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import org.jsoup.Jsoup;
import org.jsoup.safety.Safelist;
import org.springframework.util.StreamUtils;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;

public class XssRequestWrapper extends HttpServletRequestWrapper {

    private final byte[] body;

    public XssRequestWrapper(HttpServletRequest request) throws IOException {
        super(request);
        InputStream inputStream = request.getInputStream();
        byte[] rawBody = StreamUtils.copyToByteArray(inputStream);
        String bodyString = new String(rawBody, StandardCharsets.UTF_8);
        String sanitizedBody = sanitize(bodyString);
        this.body = sanitizedBody.getBytes(StandardCharsets.UTF_8);
    }

    @Override
    public String[] getParameterValues(String parameter) {
        String[] values = super.getParameterValues(parameter);
        if (values == null) {
            return null;
        }
        int count = values.length;
        String[] encodedValues = new String[count];
        for (int i = 0; i < count; i++) {
            encodedValues[i] = sanitize(values[i]);
        }
        return encodedValues;
    }

    @Override
    public String getParameter(String parameter) {
        String value = super.getParameter(parameter);
        return sanitize(value);
    }

    @Override
    public Map<String, String[]> getParameterMap() {
        Map<String, String[]> rawMap = super.getParameterMap();
        Map<String, String[]> sanitizedMap = new HashMap<>();
        for (Map.Entry<String, String[]> entry : rawMap.entrySet()) {
            String[] values = entry.getValue();
            if (values != null) {
                String[] cleanValues = new String[values.length];
                for (int i = 0; i < values.length; i++) {
                    cleanValues[i] = sanitize(values[i]);
                }
                sanitizedMap.put(sanitize(entry.getKey()), cleanValues);
            }
        }
        return Collections.unmodifiableMap(sanitizedMap);
    }

    @Override
    public String getHeader(String name) {
        String value = super.getHeader(name);
        return sanitize(value);
    }

    @Override
    public ServletInputStream getInputStream() {
        final ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(body);
        return new ServletInputStream() {
            @Override
            public boolean isFinished() {
                return byteArrayInputStream.available() == 0;
            }

            @Override
            public boolean isReady() {
                return true;
            }

            @Override
            public void setReadListener(ReadListener readListener) {
            }

            @Override
            public int read() {
                return byteArrayInputStream.read();
            }
        };
    }

    private String sanitize(String value) {
        if (value == null) {
            return null;
        }
        // Use Jsoup to clean potential HTML / script injection
        return Jsoup.clean(value, Safelist.none());
    }
}
