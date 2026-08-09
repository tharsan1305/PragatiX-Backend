package com.pragatix.infrastructure.security;

import com.pragatix.entity.SecurityAuditLog;
import com.pragatix.repository.SecurityAuditLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
public class AuditLogService {

    private static final Logger log = LoggerFactory.getLogger(AuditLogService.class);

    private final SecurityAuditLogRepository auditLogRepository;

    public AuditLogService(SecurityAuditLogRepository auditLogRepository) {
        this.auditLogRepository = auditLogRepository;
    }

    @Transactional
    public void logEvent(String eventType, String username, String ipAddress,
                         String requestUri, String httpMethod, String status, String details) {
        try {
            SecurityAuditLog auditLog = new SecurityAuditLog(
                    LocalDateTime.now(),
                    eventType,
                    username != null ? username : "ANONYMOUS",
                    ipAddress,
                    requestUri,
                    httpMethod,
                    status,
                    details
            );
            auditLogRepository.save(auditLog);
            log.info("SECURITY AUDIT LOG [{}] - User: {}, IP: {}, URI: {}, Status: {}",
                    eventType, username, ipAddress, requestUri, status);
        } catch (Exception e) {
            log.error("Failed to persist security audit log: {}", e.getMessage(), e);
        }
    }

    public void logAuthSuccess(String username, String ipAddress, String userType) {
        logEvent("LOGIN_SUCCESS", username, ipAddress, "/api/v1/auth/login", "POST", "SUCCESS", "User type: " + userType);
    }

    public void logAuthFailure(String username, String ipAddress, String reason) {
        logEvent("LOGIN_FAILURE", username, ipAddress, "/api/v1/auth/login", "POST", "FAILURE", reason);
    }

    public void logAccessDenied(String username, String ipAddress, String requestUri, String httpMethod) {
        logEvent("ACCESS_DENIED", username, ipAddress, requestUri, httpMethod, "FORBIDDEN", "Unauthorized access attempt");
    }

    public void logIpBlocked(String ipAddress, String requestUri, String httpMethod) {
        logEvent("BLOCKED_IP", "ANONYMOUS", ipAddress, requestUri, httpMethod, "BLOCKED", "Request blocked by IP filter");
    }

    public void logRateLimited(String ipAddress, String requestUri, String httpMethod) {
        logEvent("RATE_LIMITED", "ANONYMOUS", ipAddress, requestUri, httpMethod, "TOO_MANY_REQUESTS", "Bucket4j rate limit exceeded");
    }
}
