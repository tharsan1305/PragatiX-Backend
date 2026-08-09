package com.pragatix.infrastructure.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pragatix.common.response.ApiResponse;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

@Component
public class IpBlockingFilter extends OncePerRequestFilter {

    private final List<String> blockedIps;
    private final AuditLogService auditLogService;
    private final ObjectMapper objectMapper;

    public IpBlockingFilter(
            @Value("${security.ip.blocked-ips:}") String blockedIpsString,
            AuditLogService auditLogService,
            ObjectMapper objectMapper) {
        this.blockedIps = StringUtils.hasText(blockedIpsString)
                ? Arrays.stream(blockedIpsString.split(","))
                        .map(String::trim)
                        .filter(StringUtils::hasText)
                        .toList()
                : List.of();
        this.auditLogService = auditLogService;
        this.objectMapper = objectMapper;
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain) throws ServletException, IOException {

        String clientIp = extractClientIp(request);

        if (!blockedIps.isEmpty() && isIpBlocked(clientIp)) {
            auditLogService.logIpBlocked(clientIp, request.getRequestURI(), request.getMethod());

            response.setStatus(HttpStatus.FORBIDDEN.value());
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);

            ApiResponse<Void> apiResponse = ApiResponse.error("Access denied: Your IP address has been blocked.");
            response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
            return;
        }

        filterChain.doFilter(request, response);
    }

    private boolean isIpBlocked(String clientIp) {
        return blockedIps.contains(clientIp);
    }

    public static String extractClientIp(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (StringUtils.hasText(xForwardedFor)) {
            return xForwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
