package br.unifor.ppgia.cloud.core.comm;

import br.unifor.ppgia.cloud.core.DetoursContext;
import br.unifor.ppgia.cloud.core.comm.defaultimpl.DefaultChannelProvider;

public abstract class ChannelProvider {

	private static final String _CHANNEL_PROVIDER_ = "channel.provider";

	private static ChannelProvider instance = null;

	public enum EventType {
		BLANK_EVT("blank"), REQUEST_EVT("request-service"), CLOSE_EVT("close"), 
		PING_EVT("ping"), LOOPBACK_EVT("loop"), TERMINATE_EVT("terminate");
		
		String code;
		
		EventType(String code) {
			this.code = code;
		}
		
		public String getCode() {
			return code;
		}
	}

	public static ChannelProvider getInstance() {
		DetoursContext context = DetoursContext.getInstance();

		String providerName = context.getProperty(_CHANNEL_PROVIDER_);

		try {
			Class<?> clazz = Class.forName(providerName);
			instance = (ChannelProvider) clazz.newInstance();
		} catch (Exception e) {
			e.printStackTrace();
			// XXX Log the problem
			instance = new DefaultChannelProvider();
		}
		return instance;
	}

	public abstract Channel createChannel(String endpoint);
	
	public abstract Channel createChannel(String protocol, String address);
	
	public abstract Channel createChannel(String protocol, String address, int port);

	public abstract Event getEvent(EventType type);
}
