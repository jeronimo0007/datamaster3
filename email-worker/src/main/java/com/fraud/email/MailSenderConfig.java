package com.fraud.email;

import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.JavaMailSenderImpl;

@Configuration
public class MailSenderConfig {

    @Bean
    @ConditionalOnExpression("T(org.springframework.util.StringUtils).hasText('${spring.mail.host:}')")
    JavaMailSender javaMailSender(org.springframework.core.env.Environment env) {
        JavaMailSenderImpl sender = new JavaMailSenderImpl();
        int port = env.getProperty("spring.mail.port", Integer.class, 587);
        boolean ssl = env.getProperty("spring.mail.properties.mail.smtp.ssl.enable", Boolean.class, port == 465);

        sender.setHost(env.getProperty("spring.mail.host", "").trim());
        sender.setPort(port);
        sender.setUsername(env.getProperty("spring.mail.username", ""));
        sender.setPassword(env.getProperty("spring.mail.password", ""));

        java.util.Properties props = sender.getJavaMailProperties();
        props.put("mail.transport.protocol", "smtp");
        props.put("mail.smtp.auth", "true");
        if (ssl) {
            props.put("mail.smtp.ssl.enable", "true");
            props.put("mail.smtp.socketFactory.port", String.valueOf(port));
            props.put("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
            props.put("mail.smtp.starttls.enable", "false");
        } else {
            props.put("mail.smtp.ssl.enable", "false");
            props.put(
                    "mail.smtp.starttls.enable",
                    env.getProperty("spring.mail.properties.mail.smtp.starttls.enable", "true"));
        }
        return sender;
    }
}
