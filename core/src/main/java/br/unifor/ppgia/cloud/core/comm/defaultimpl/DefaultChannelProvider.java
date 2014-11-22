package br.unifor.ppgia.cloud.core.comm.defaultimpl;

import java.util.HashMap;
import java.util.Map;

import org.zeromq.ZMQ;

import br.unifor.ppgia.cloud.core.comm.Channel;
import br.unifor.ppgia.cloud.core.comm.ChannelProvider;
import br.unifor.ppgia.cloud.core.comm.Event;

public class DefaultChannelProvider extends ChannelProvider {
	
	ZMQ.Context zContext = ZMQ.context(1);
	
	@Override
	public Channel createChannel(String endpoint) {
		DefaultChannel channel = new DefaultChannel(endpoint);
		channel.setUpContext(zContext);
		return channel;
	}
	
	@Override
	public Event getEvent(EventType type) {
		Event evt = null;
		
		switch(type) {
		case PING_EVT:
		case PONG_EVT:
		case LOOPBACK_EVT:
			evt = createEvent("control", type.getCode());
			break;
		case BLANK_EVT:
			evt = createBlankEvent();
			break;
		default:
			evt = createEvent("action", type.getCode());
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

	@Override
	public void releaseResources() {
		//zContext.term();
		System.out.println("Context released...");

	}
}
