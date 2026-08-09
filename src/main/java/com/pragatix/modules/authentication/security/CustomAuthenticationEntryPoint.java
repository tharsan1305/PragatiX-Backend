package com.pragatix.modules.authentication.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pragatix.common.response.ApiResponse;
import com.pragatix.infrastructure.security.AuditLogService;
import com.pragatix.infrastructure.security.IpBlockingFilter;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class CustomAuthenticationEntryPoint implements AuthenticationEntryPoint {

    private final AuditLogService auditLogService;
    private final ObjectMapper objectMapper;

    public CustomAuthenticationEntryPoint(AuditLogService auditLogService, ObjectMapper objectMapper) {
        this.auditLogService = auditLogService;
        this.objectMapper = objectMapper;
    }

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException) throws IOException, ServletException {
        String clientIp = IpBlockingFilter.extractClientIp(request);
        auditLogService.logEvent("UNAUTHORIZED_ACCESS", "ANONYMOUS", clientIp, request.getRequestURI(), request.getMethod(), "UNAUTHORIZED", authException.getMessage());

        response.setStatus(HttpStatus.UNAUTHORIZED.value());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);

        ApiResponse<Void> apiResponse = ApiResponse.error("Unauthorized. Please login.");
        response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
    }
}
