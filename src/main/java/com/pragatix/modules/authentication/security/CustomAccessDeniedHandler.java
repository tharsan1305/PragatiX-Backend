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
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class CustomAccessDeniedHandler implements AccessDeniedHandler {

    private final AuditLogService auditLogService;
    private final ObjectMapper objectMapper;

    public CustomAccessDeniedHandler(AuditLogService auditLogService, ObjectMapper objectMapper) {
        this.auditLogService = auditLogService;
        this.objectMapper = objectMapper;
    }

    @Override
    public void handle(HttpServletRequest request, HttpServletResponse response, AccessDeniedException accessDeniedException) throws IOException, ServletException {
        String clientIp = IpBlockingFilter.extractClientIp(request);
        String username = SecurityContextHolder.getContext().getAuthentication() != null
                ? SecurityContextHolder.getContext().getAuthentication().getName()
                : "ANONYMOUS";

        auditLogService.logAccessDenied(username, clientIp, request.getRequestURI(), request.getMethod());

        response.setStatus(HttpStatus.FORBIDDEN.value());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);

        ApiResponse<Void> apiResponse = ApiResponse.error("Forbidden. You don't have permission.");
        response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
    }
}
