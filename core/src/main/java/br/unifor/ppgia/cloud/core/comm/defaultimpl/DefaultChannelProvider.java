package br.unifor.ppgia.cloud.core.comm.defaultimpl;

import java.util.HashMap;
import java.util.Map;

import br.unifor.ppgia.cloud.core.comm.Channel;
import br.unifor.ppgia.cloud.core.comm.ChannelProvider;
import br.unifor.ppgia.cloud.core.comm.Event;

public class DefaultChannelProvider extends ChannelProvider {
	
	@Override
	public Channel createChannel(String endpoint) {
		return new DefaultChannel(endpoint);
	}

	@Override
	public Channel createChannel(String protocol, String address) {
		return new DefaultChannel(protocol, address);
	}

	@Override
	public Channel createChannel(String protocol, String address, int port) {
		return new DefaultChannel(protocol, address, port);
	}
	
	@Override
	public Event getEvent(EventType type) {
		Event evt = null;
		
		switch(type) {
		case REQUEST_EVT:
		case CLOSE_EVT:
			evt = createEvent("action", type.getCode());
			break;
		case PING_EVT:
		case LOOPBACK_EVT:
		case TERMINATE_EVT:
			evt = createEvent("control", type.getCode());
			break;
		case BLANK_EVT:
		default:
			evt = createBlankEvent();
		}
		return evt;
	}

	private Event createEvent(String key, String value) {
		// Creating REQUEST EVENT
		Event evt = new DefaultIOEvent();
		Map<String, String> data = new HashMap<String, String>();
		data.put(key, value);
		evt.addInfo(data);
		return evt;
	}
	
	private Event createBlankEvent() {
		return new DefaultIOEvent();
	}
}
